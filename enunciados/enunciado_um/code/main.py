from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any
from collections import Counter

from dotenv import load_dotenv
from github_gql import graphql_request

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

# Query atualizada para incluir RQ04 e RQ05
QUERY_TOP100_BASIC = """
query($q: String!, $n: Int!) {
  rateLimit { cost remaining resetAt }
  search(type: REPOSITORY, query: $q, first: $n) {
    nodes {
      ... on Repository {
        name
        owner { login }
        nameWithOwner
        url
        createdAt
        updatedAt
        stargazerCount
        primaryLanguage { name }
      }
    }
  }
}
"""

def get_top_repos_basic(n: int = 100) -> list[dict[str, Any]]:
    search_query = "stars:>0 sort:stars-desc"
    result = graphql_request(QUERY_TOP100_BASIC, {"q": search_query, "n": n})
    repos: list[dict[str, Any]] = []
    for r in result["data"]["search"]["nodes"]:
        repos.append(
            {
                "owner": r["owner"]["login"],
                "name": r["name"],
                "full_name": r["nameWithOwner"],
                "url": r["url"],
                "stars": int(r["stargazerCount"]),
                "created_at": datetime.fromisoformat(r["createdAt"].replace("Z", "+00:00")),
                "updated_at": datetime.fromisoformat(r["updatedAt"].replace("Z", "+00:00")),
                "language": r["primaryLanguage"]["name"] if r["primaryLanguage"] else "Unknown",
            }
        )
    return repos

def build_metrics_query(batch: list[dict[str, Any]]) -> str:
    parts = ["query {", "rateLimit { cost remaining resetAt }"]
    for i, repo in enumerate(batch):
        owner = repo["owner"].replace('"', '\\"')
        name = repo["name"].replace('"', '\\"')
        # Adicionado total de issues e issues fechadas para RQ06
        parts.append(
            f'''
            r{i}: repository(owner: "{owner}", name: "{name}") {{
              pullRequests(states: MERGED) {{ totalCount }}
              releases {{ totalCount }}
              all_issues: issues {{ totalCount }}
              closed_issues: issues(states: CLOSED) {{ totalCount }}
            }}
            '''
        )
    parts.append("}")
    return "\n".join(parts)

def fetch_metrics_batch(batch: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    query = build_metrics_query(batch)
    result = graphql_request(query, None)
    data = result["data"]

    metrics: dict[str, dict[str, Any]] = {}
    for i, repo in enumerate(batch):
        alias = f"r{i}"
        node = data.get(alias)
        key = repo["full_name"]

        if node is None:
            metrics[key] = {"merged_prs": 0, "releases": 0, "total_issues": 0, "closed_issues": 0}
            continue

        metrics[key] = {
            "merged_prs": int(node["pullRequests"]["totalCount"]),
            "releases": int(node["releases"]["totalCount"]),
            "total_issues": int(node["all_issues"]["totalCount"]),
            "closed_issues": int(node["closed_issues"]["totalCount"]),
        }
    return metrics

def fetch_metrics_with_retry(batch: list[dict[str, Any]], max_attempts: int = 3) -> dict[str, dict[str, Any]]:
    for attempt in range(max_attempts):
        try:
            return fetch_metrics_batch(batch)
        except Exception:
            if attempt == max_attempts - 1:
                return {r["full_name"]: {"merged_prs": 0, "releases": 0, "total_issues": 0, "closed_issues": 0} for r in batch}
            time.sleep(2 ** attempt)

def main() -> None:
    if not os.getenv("GITHUB_TOKEN"):
        raise RuntimeError(f"GITHUB_TOKEN não carregou. Confere o .env em: {ENV_PATH}")

    try:
        num_repos = int(input("Quantos repositórios deseja buscar? (padrão: 100): ") or "100")
    except ValueError:
        num_repos = 100

    num_repos = max(1, min(num_repos, 1000))
    print(f"\n📊 Analisando {num_repos} repositórios...")

    repos = get_top_repos_basic(num_repos)
    
    # Coleta de métricas em batches
    batch_size = 4
    all_metrics = {}
    total_batches = (len(repos) + batch_size - 1) // batch_size

    for i in range(0, len(repos), batch_size):
        batch = repos[i : i + batch_size]
        print(f"[{i//batch_size + 1}/{total_batches}] Coletando métricas detalhadas... ", end="", flush=True)
        m = fetch_metrics_with_retry(batch)
        all_metrics.update(m)
        print("✅")
        time.sleep(0.5)

    now = datetime.now(timezone.utc)
    
    # Listas para cálculos
    ages = []
    merged_prs = []
    releases = []
    update_intervals = []
    languages = []
    issue_ratios = []

    for r in repos:
        m = all_metrics.get(r["full_name"], {"merged_prs": 0, "releases": 0, "total_issues": 0, "closed_issues": 0})
        
        # RQ01
        ages.append((now - r["created_at"]).days)
        # RQ02 e RQ03
        merged_prs.append(m["merged_prs"])
        releases.append(m["releases"])
        # RQ04: Tempo desde a última atualização (em dias)
        update_intervals.append(max(0, (now - r["updated_at"]).days))
        # RQ05: Linguagens
        languages.append(r["language"])
        # RQ06: Razão de issues fechadas
        if m["total_issues"] > 0:
            issue_ratios.append(m["closed_issues"] / m["total_issues"])
        else:
            issue_ratios.append(0.0)

    print("\n" + "="*40)
    print("       RELATÓRIO FINAL DE MINERAÇÃO")
    print("="*40)
    
    print(f"RQ01. Mediana Idade: {median(ages):.0f} dias")
    print(f"RQ02. Mediana PRs Merged: {median(merged_prs):.0f}")
    print(f"RQ03. Mediana Releases: {median(releases):.0f}")
    print(f"RQ04. Mediana dias desde a última atualização: {median(update_intervals):.0f} dias")

    lang_counts = Counter(languages).most_common(5)
    print(f"RQ05. Top 5 Linguagens: {', '.join([f'{l}: {c}' for l, c in lang_counts])}")
    
    avg_issue_ratio = (sum(issue_ratios) / len(issue_ratios)) * 100
    print(f"RQ06. Percentual médio de Issues Fechadas: {avg_issue_ratio:.2f}%")
    print("="*40)

if __name__ == "__main__":
    main()