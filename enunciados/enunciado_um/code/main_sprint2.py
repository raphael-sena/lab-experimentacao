from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from github_gql import graphql_request

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

QUERY_SEARCH_PAGE = """
query($q: String!, $n: Int!, $cursor: String) {
  rateLimit { cost remaining resetAt }
  search(type: REPOSITORY, query: $q, first: $n, after: $cursor) {
    pageInfo {
      hasNextPage
      endCursor
    }
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


def get_top_repos_paginated(target: int = 1000) -> list[dict[str, Any]]:
    """Busca os repositórios mais estrelados via paginação cursor-based."""
    search_query = "stars:>0 sort:stars-desc"
    page_size = 100
    repos: list[dict[str, Any]] = []
    cursor: str | None = None
    page = 0

    while len(repos) < target:
        remaining_needed = target - len(repos)
        fetch_n = min(page_size, remaining_needed)

        page += 1
        print(f"  [página {page}] buscando {fetch_n} repositórios... ", end="", flush=True)

        result = graphql_request(
            QUERY_SEARCH_PAGE,
            {"q": search_query, "n": fetch_n, "cursor": cursor},
        )

        search = result["data"]["search"]
        page_info = search["pageInfo"]

        for r in search["nodes"]:
            repos.append(
                {
                    "owner": r["owner"]["login"],
                    "name": r["name"],
                    "full_name": r["nameWithOwner"],
                    "url": r["url"],
                    "stars": int(r["stargazerCount"]),
                    "created_at": datetime.fromisoformat(
                        r["createdAt"].replace("Z", "+00:00")
                    ),
                    "updated_at": datetime.fromisoformat(
                        r["updatedAt"].replace("Z", "+00:00")
                    ),
                    "language": (
                        r["primaryLanguage"]["name"]
                        if r["primaryLanguage"]
                        else "Unknown"
                    ),
                }
            )

        print(f"✅  (total até agora: {len(repos)})")

        if not page_info["hasNextPage"]:
            print("  Não há mais páginas disponíveis.")
            break

        cursor = page_info["endCursor"]
        time.sleep(0.3)

    return repos[:target]

def build_metrics_query(batch: list[dict[str, Any]]) -> str:
    parts = ["query {", "rateLimit { cost remaining resetAt }"]
    for i, repo in enumerate(batch):
        owner = repo["owner"].replace('"', '\\"')
        name = repo["name"].replace('"', '\\"')
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
        node = data.get(f"r{i}")
        key = repo["full_name"]
        if node is None:
            metrics[key] = {
                "merged_prs": 0,
                "releases": 0,
                "total_issues": 0,
                "closed_issues": 0,
            }
            continue
        metrics[key] = {
            "merged_prs": int(node["pullRequests"]["totalCount"]),
            "releases": int(node["releases"]["totalCount"]),
            "total_issues": int(node["all_issues"]["totalCount"]),
            "closed_issues": int(node["closed_issues"]["totalCount"]),
        }
    return metrics


def fetch_metrics_with_retry(
    batch: list[dict[str, Any]], max_attempts: int = 3
) -> dict[str, dict[str, Any]]:
    for attempt in range(max_attempts):
        try:
            return fetch_metrics_batch(batch)
        except Exception:
            if attempt == max_attempts - 1:
                return {
                    r["full_name"]: {
                        "merged_prs": 0,
                        "releases": 0,
                        "total_issues": 0,
                        "closed_issues": 0,
                    }
                    for r in batch
                }
            time.sleep(2**attempt)

def main() -> None:
    if not os.getenv("GITHUB_TOKEN"):
        raise RuntimeError(
            f"GITHUB_TOKEN não carregou. Confere o .env em: {ENV_PATH}"
        )

    try:
        num_repos = int(
            input("Quantos repositórios deseja buscar? (padrão: 1000): ") or "1000"
        )
    except ValueError:
        num_repos = 1000

    num_repos = max(1, min(num_repos, 1000))
    print(f"\n📄 Coletando {num_repos} repositórios...\n")

    repos = get_top_repos_paginated(num_repos)
    print(f"\nTotal de repositórios coletados: {len(repos)}")

    batch_size = 4
    all_metrics: dict[str, dict[str, Any]] = {}
    total_batches = (len(repos) + batch_size - 1) // batch_size

    print(f"\n🔍 Coletando métricas detalhadas ({total_batches} batches)...\n")
    for i in range(0, len(repos), batch_size):
        batch = repos[i : i + batch_size]
        batch_num = i // batch_size + 1
        print(f"  [{batch_num}/{total_batches}] ", end="", flush=True)
        m = fetch_metrics_with_retry(batch)
        all_metrics.update(m)
        print("✅")
        time.sleep(0.5)

    print(f"\n✅ {len(repos)} repositórios coletados com sucesso.")


if __name__ == "__main__":
    main()
