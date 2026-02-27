from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

from dotenv import load_dotenv

from github_gql import graphql_request

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

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
        stargazerCount
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
            }
        )
    return repos

def build_metrics_query(batch: list[dict[str, Any]]) -> str:
    # Monta uma query com aliases: r0, r1, r2...
    parts = ["query {", "rateLimit { cost remaining resetAt }"]
    for i, repo in enumerate(batch):
        owner = repo["owner"].replace('"', '\\"')
        name = repo["name"].replace('"', '\\"')
        parts.append(
            f'''
            r{i}: repository(owner: "{owner}", name: "{name}") {{
              pullRequests(states: MERGED) {{ totalCount }}
              releases {{ totalCount }}
            }}
            '''
        )
    parts.append("}")
    return "\n".join(parts)

def fetch_metrics_batch(batch: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    query = build_metrics_query(batch)
    result = graphql_request(query, None)
    data = result["data"]

    metrics: dict[str, dict[str, int]] = {}
    for i, repo in enumerate(batch):
        alias = f"r{i}"
        node = data.get(alias)
        key = repo["full_name"]

        if node is None:
            metrics[key] = {"merged_prs_total": 0, "releases_total": 0}
            continue

        metrics[key] = {
            "merged_prs_total": int(node["pullRequests"]["totalCount"]),
            "releases_total": int(node["releases"]["totalCount"]),
        }
    return metrics

def age_in_days(created_at: datetime, now: datetime) -> int:
    delta = now - created_at
    return max(0, int(delta.total_seconds() // 86400))

def fetch_metrics_with_retry(batch: list[dict[str, Any]], max_attempts: int = 3) -> dict[str, dict[str, int]]:
    """Busca métricas com retry automático em caso de falha parcial."""
    for attempt in range(max_attempts):
        try:
            return fetch_metrics_batch(batch)
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"⚠️  Falha após {max_attempts} tentativas no batch. Retornando zeros.")
                return {r["full_name"]: {"merged_prs_total": 0, "releases_total": 0} for r in batch}
            wait_time = 2 ** attempt
            print(f"  ⚠️  Retry em {wait_time}s... (tentativa {attempt + 1}/{max_attempts})")
            time.sleep(wait_time)

def main() -> None:
    if not os.getenv("GITHUB_TOKEN"):
        raise RuntimeError(f"GITHUB_TOKEN não carregou. Confere o .env em: {ENV_PATH}")

    # Entrada do usuário
    try:
        num_repos = int(input("Quantos repositórios deseja buscar? (padrão: 100): ") or "100")
    except ValueError:
        num_repos = 100

    num_repos = max(1, min(num_repos, 1000))  # Limita entre 1 e 1000
    print(f"\n📊 Buscando {num_repos} repositórios...")

    repos = get_top_repos_basic(num_repos)
    print(f"✅ {len(repos)} repositórios encontrados\n")

    # Batches adaptáveis: quanto maior o número de repos, batches maiores
    # Evita timeout com query muito grande (máx 4 repos por batch para segurança)
    batch_size = min(4, max(1, 10 - (num_repos // 200)))
    all_metrics: dict[str, dict[str, int]] = {}

    total_batches = (len(repos) + batch_size - 1) // batch_size

    for i in range(0, len(repos), batch_size):
        batch = repos[i : i + batch_size]
        batch_num = i // batch_size + 1
        print(f"[{batch_num}/{total_batches}] Buscando métricas ({len(batch)} repos)... ", end="", flush=True)
        m = fetch_metrics_with_retry(batch)
        all_metrics.update(m)
        print("✅")

        # Rate limit awareness: pequena pausa entre batches
        if batch_num < total_batches:
            time.sleep(0.5)

    # Junta no objeto final
    for r in repos:
        m = all_metrics.get(r["full_name"], {"merged_prs_total": 0, "releases_total": 0})
        r["merged_prs_total"] = m["merged_prs_total"]
        r["releases_total"] = m["releases_total"]

    now = datetime.now(timezone.utc)

    # RQ01: idade (dias) desde criação
    ages_days = [age_in_days(r["created_at"], now) for r in repos]
    # RQ02: merged PRs
    merged_prs = [r["merged_prs_total"] for r in repos]
    # RQ03: releases
    releases = [r["releases_total"] for r in repos]

    print(f"\n=== Resultados (Top {num_repos}) ===")
    print(f"RQ01 mediana idade: {median(ages_days)} dias e {median(ages_days) // 365} anos")
    print(f"RQ02 mediana PRs aceitas (MERGED): {int(median(merged_prs))}")
    print(f"RQ03 mediana releases: {int(median(releases))}")

    print("\nAmostra (5 primeiros):")
    for r in repos[:5]:
        print(f"- {r['full_name']} | mergedPRs={r['merged_prs_total']} | releases={r['releases_total']}")

if __name__ == "__main__":
    main()