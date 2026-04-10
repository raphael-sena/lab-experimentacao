from __future__ import annotations

import argparse
import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from github_gql import graphql_request

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_CSV = OUTPUT_DIR / "repo_measurements_1000.csv"


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(ENV_PATH)

QUERY_SEARCH_PAGE = """
query($q: String!, $n: Int!, $cursor: String) {
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
        stargazerCount
        createdAt
        updatedAt
        primaryLanguage { name }
      }
    }
  }
}
"""


def fetch_top_java_repositories(target: int) -> list[dict[str, Any]]:
    query = "language:Java stars:>0 sort:stars-desc"
    page_size = 100
    repos: list[dict[str, Any]] = []
    cursor: str | None = None

    while len(repos) < target:
        fetch_n = min(page_size, target - len(repos))
        page_no = len(repos) // page_size + 1
        print(f"[GitHub] page {page_no}: fetching {fetch_n} repos...")

        result = graphql_request(
            QUERY_SEARCH_PAGE,
            {"q": query, "n": fetch_n, "cursor": cursor},
        )

        search = result["data"]["search"]
        for node in search["nodes"]:
            created_at = datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(node["updatedAt"].replace("Z", "+00:00"))
            repos.append(
                {
                    "owner": node["owner"]["login"],
                    "name": node["name"],
                    "full_name": node["nameWithOwner"],
                    "url": node["url"],
                    "stars": int(node["stargazerCount"]),
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "language": (node.get("primaryLanguage") or {}).get("name", "Unknown"),
                }
            )

        if not search["pageInfo"]["hasNextPage"]:
            break

        cursor = search["pageInfo"]["endCursor"]

    return repos[:target]


def build_metrics_query(batch: list[dict[str, Any]]) -> str:
    parts = ["query {"]
    for i, repo in enumerate(batch):
        owner = repo["owner"].replace('"', '\\"')
        name = repo["name"].replace('"', '\\"')
        parts.append(
            f'''
            r{i}: repository(owner: "{owner}", name: "{name}") {{
              pullRequests(states: MERGED) {{ totalCount }}
              releases {{ totalCount }}
              allIssues: issues {{ totalCount }}
              closedIssues: issues(states: CLOSED) {{ totalCount }}
            }}
            '''
        )
    parts.append("}")
    return "\n".join(parts)


def fetch_metrics_batch(batch: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    query = build_metrics_query(batch)
    result = graphql_request(query)
    data = result["data"]

    metrics: dict[str, dict[str, int]] = {}
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
            "total_issues": int(node["allIssues"]["totalCount"]),
            "closed_issues": int(node["closedIssues"]["totalCount"]),
        }

    return metrics


def fetch_metrics_with_retry(
    batch: list[dict[str, Any]],
    max_attempts: int,
) -> dict[str, dict[str, int]]:
    for attempt in range(1, max_attempts + 1):
        try:
            return fetch_metrics_batch(batch)
        except Exception as ex:
            if attempt == max_attempts:
                print(f"[warn] batch failed after {max_attempts} attempts: {ex}")
                return {
                    repo["full_name"]: {
                        "merged_prs": 0,
                        "releases": 0,
                        "total_issues": 0,
                        "closed_issues": 0,
                    }
                    for repo in batch
                }
            sleep_seconds = 2 ** (attempt - 1)
            print(f"[retry] batch attempt {attempt}/{max_attempts} failed: {ex}; sleeping {sleep_seconds}s")
            time.sleep(sleep_seconds)

    return {}


def write_output_csv(rows: list[dict[str, Any]], csv_path: Path) -> Path:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []

    with csv_path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    return csv_path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lab02 Sprint2: collect metrics for top Java repositories and export CSV"
    )
    parser.add_argument(
        "--target",
        type=int,
        default=1000,
        help="Number of repositories to collect (max: 1000).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Number of repositories per GraphQL metrics query batch.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=3,
        help="Max retry attempts for each metrics batch.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.4,
        help="Seconds to sleep between batches.",
    )
    return parser.parse_args()


def main() -> None:
    if not os.getenv("GITHUB_TOKEN"):
        raise RuntimeError(f"GITHUB_TOKEN not found. Configure {ENV_PATH}")

    args = parse_arguments()
    target = max(1, min(args.target, 1000))
    batch_size = max(1, min(args.batch_size, 20))
    max_attempts = max(1, min(args.max_attempts, 8))

    repos = fetch_top_java_repositories(target=target)
    print(f"[info] repos collected: {len(repos)}")

    all_metrics: dict[str, dict[str, int]] = {}
    total_batches = (len(repos) + batch_size - 1) // batch_size
    for i in range(0, len(repos), batch_size):
        batch = repos[i : i + batch_size]
        batch_no = i // batch_size + 1
        print(f"[metrics] batch {batch_no}/{total_batches}")
        metrics = fetch_metrics_with_retry(batch, max_attempts=max_attempts)
        all_metrics.update(metrics)
        if args.sleep > 0:
            time.sleep(args.sleep)

    now = datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []

    for repo in repos:
        m = all_metrics.get(
            repo["full_name"],
            {
                "merged_prs": 0,
                "releases": 0,
                "total_issues": 0,
                "closed_issues": 0,
            },
        )
        total_issues = m["total_issues"]
        closed_issues = m["closed_issues"]
        rows.append(
            {
                "full_name": repo["full_name"],
                "url": repo["url"],
                "language": repo["language"],
                "stars": repo["stars"],
                "created_at": repo["created_at"].strftime("%Y-%m-%d"),
                "updated_at": repo["updated_at"].strftime("%Y-%m-%d"),
                "age_days": (now - repo["created_at"]).days,
                "days_since_update": max(0, (now - repo["updated_at"]).days),
                "merged_prs": m["merged_prs"],
                "releases": m["releases"],
                "total_issues": total_issues,
                "closed_issues": closed_issues,
                "open_issues": max(0, total_issues - closed_issues),
                "closed_issue_ratio": round(closed_issues / total_issues, 4) if total_issues > 0 else 0.0,
            }
        )

    csv_path = write_output_csv(rows, OUTPUT_CSV)
    print("\nSprint 2 finished.")
    print(f"- Consolidated CSV: {csv_path}")


if __name__ == "__main__":
    main()
