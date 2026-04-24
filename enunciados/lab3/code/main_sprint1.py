from __future__ import annotations

import argparse
import csv
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from github_gql import graphql_request, load_env_file

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "output"

SELECTED_REPOS_CSV = OUTPUT_DIR / "repos_selected.csv"
PRS_DATASET_CSV = OUTPUT_DIR / "prs_sprint1.csv"
FAILED_REPOS_CSV = OUTPUT_DIR / "failed_repos.csv"

load_env_file(ENV_PATH)

QUERY_REPOS_PAGE = """
query($q: String!, $n: Int!, $cursor: String) {
  search(type: REPOSITORY, query: $q, first: $n, after: $cursor) {
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on Repository {
        nameWithOwner
        url
        stargazerCount
        pullRequests(states: MERGED) { totalCount }
        pullRequestsClosedOnly: pullRequests(states: CLOSED) { totalCount }
      }
    }
  }
}
"""

QUERY_PULL_REQUESTS_PAGE = """
query($owner: String!, $name: String!, $n: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequests(
      first: $n,
      after: $cursor,
      states: [MERGED, CLOSED],
      orderBy: {field: CREATED_AT, direction: DESC}
    ) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        number
        url
        state
        createdAt
        mergedAt
        closedAt
        changedFiles
        additions
        deletions
        body
        reviews { totalCount }
        participants { totalCount }
        comments { totalCount }
      }
    }
  }
}
"""


@dataclass
class SelectedRepo:
    full_name: str
    url: str
    stars: int
    merged_prs: int
    closed_prs: int
    total_prs_merged_closed: int


@dataclass
class PullRequestRecord:
    repo_full_name: str
    repo_url: str
    pr_number: int
    pr_url: str
    final_status: str
    created_at: str
    ended_at: str
    review_time_hours: float
    review_count: int
    changed_files: int
    additions: int
    deletions: int
    description_char_count: int
    participants_count: int
    comments_count: int


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def fetch_selected_repositories(target: int, min_prs: int) -> list[SelectedRepo]:
    selected: list[SelectedRepo] = []
    cursor: str | None = None
    page_size = 100

    # Busca repositórios mais populares por estrelas.
    search_query = "stars:>1 sort:stars-desc"

    while len(selected) < target:
        print(f"[repos] coletando página; selecionados até agora: {len(selected)}/{target}")
        result = graphql_request(
            QUERY_REPOS_PAGE,
            {"q": search_query, "n": page_size, "cursor": cursor},
            max_retries=1,
        )

        search = result["data"]["search"]
        nodes = search["nodes"]

        for node in nodes:
            merged_prs = int(node["pullRequests"]["totalCount"])
            closed_prs = int(node["pullRequestsClosedOnly"]["totalCount"])
            total_prs = merged_prs + closed_prs

            if total_prs < min_prs:
                continue

            selected.append(
                SelectedRepo(
                    full_name=node["nameWithOwner"],
                    url=node["url"],
                    stars=int(node["stargazerCount"]),
                    merged_prs=merged_prs,
                    closed_prs=closed_prs,
                    total_prs_merged_closed=total_prs,
                )
            )

            if len(selected) >= target:
                break

        if len(selected) >= target:
            break

        if not search["pageInfo"]["hasNextPage"]:
            break

        cursor = search["pageInfo"]["endCursor"]

    return selected[:target]


def fetch_repository_prs(
    repo: SelectedRepo,
    *,
    page_size: int,
    max_prs_per_repo: int,
    sleep_between_pages: float,
) -> list[PullRequestRecord]:
    owner, name = repo.full_name.split("/", 1)
    cursor: str | None = None
    dataset_rows: list[PullRequestRecord] = []

    while True:
        try:
            result = graphql_request(
                QUERY_PULL_REQUESTS_PAGE,
                {
                    "owner": owner,
                    "name": name,
                    "n": page_size,
                    "cursor": cursor,
                },
                max_retries=1,
            )
        except Exception as ex:
            raise RuntimeError(f"falha_na_coleta_prs: {ex}") from ex

        repository = result["data"].get("repository")
        if repository is None:
            break

        pull_requests = repository["pullRequests"]

        for pr in pull_requests["nodes"]:
            final_status = pr["state"]
            review_count = int(pr["reviews"]["totalCount"])
            if review_count < 1:
                continue

            created_at_dt = _parse_datetime(pr["createdAt"])
            ended_at_raw = pr["mergedAt"] if final_status == "MERGED" else pr["closedAt"]
            ended_at_dt = _parse_datetime(ended_at_raw)
            if created_at_dt is None or ended_at_dt is None:
                continue

            review_time_hours = (ended_at_dt - created_at_dt).total_seconds() / 3600.0
            if review_time_hours <= 1.0:
                continue

            dataset_rows.append(
                PullRequestRecord(
                    repo_full_name=repo.full_name,
                    repo_url=repo.url,
                    pr_number=int(pr["number"]),
                    pr_url=pr["url"],
                    final_status=final_status,
                    created_at=pr["createdAt"],
                    ended_at=ended_at_raw,
                    review_time_hours=round(review_time_hours, 4),
                    review_count=review_count,
                    changed_files=int(pr["changedFiles"]),
                    additions=int(pr["additions"]),
                    deletions=int(pr["deletions"]),
                    description_char_count=len(pr.get("body") or ""),
                    participants_count=int(pr["participants"]["totalCount"]),
                    comments_count=int(pr["comments"]["totalCount"]),
                )
            )

            if max_prs_per_repo > 0 and len(dataset_rows) >= max_prs_per_repo:
                return dataset_rows

        if not pull_requests["pageInfo"]["hasNextPage"]:
            break

        cursor = pull_requests["pageInfo"]["endCursor"]
        if sleep_between_pages > 0:
            time.sleep(sleep_between_pages)

    return dataset_rows


def save_selected_repos_csv(repos: list[SelectedRepo], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "full_name",
        "url",
        "stars",
        "merged_prs",
        "closed_prs",
        "total_prs_merged_closed",
    ]

    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for repo in repos:
            writer.writerow(
                {
                    "full_name": repo.full_name,
                    "url": repo.url,
                    "stars": repo.stars,
                    "merged_prs": repo.merged_prs,
                    "closed_prs": repo.closed_prs,
                    "total_prs_merged_closed": repo.total_prs_merged_closed,
                }
            )

    return path


def load_selected_repos_csv(path: Path) -> list[SelectedRepo]:
    if not path.exists():
        return []

    repos: list[SelectedRepo] = []
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        for row in reader:
            repos.append(
                SelectedRepo(
                    full_name=row["full_name"],
                    url=row["url"],
                    stars=int(row["stars"]),
                    merged_prs=int(row["merged_prs"]),
                    closed_prs=int(row["closed_prs"]),
                    total_prs_merged_closed=int(row["total_prs_merged_closed"]),
                )
            )

    return repos


def save_pr_dataset_csv(rows: list[PullRequestRecord], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "repo_full_name",
        "repo_url",
        "pr_number",
        "pr_url",
        "final_status",
        "created_at",
        "ended_at",
        "review_time_hours",
        "review_count",
        "changed_files",
        "additions",
        "deletions",
        "description_char_count",
        "participants_count",
        "comments_count",
    ]

    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "repo_full_name": row.repo_full_name,
                    "repo_url": row.repo_url,
                    "pr_number": row.pr_number,
                    "pr_url": row.pr_url,
                    "final_status": row.final_status,
                    "created_at": row.created_at,
                    "ended_at": row.ended_at,
                    "review_time_hours": row.review_time_hours,
                    "review_count": row.review_count,
                    "changed_files": row.changed_files,
                    "additions": row.additions,
                    "deletions": row.deletions,
                    "description_char_count": row.description_char_count,
                    "participants_count": row.participants_count,
                    "comments_count": row.comments_count,
                }
            )

    return path


def ensure_pr_dataset_header(path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "repo_full_name",
        "repo_url",
        "pr_number",
        "pr_url",
        "final_status",
        "created_at",
        "ended_at",
        "review_time_hours",
        "review_count",
        "changed_files",
        "additions",
        "deletions",
        "description_char_count",
        "participants_count",
        "comments_count",
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()


def append_pr_dataset_rows(rows: list[PullRequestRecord], path: Path) -> int:
    if not rows:
        return 0

    ensure_pr_dataset_header(path)
    fieldnames = [
        "repo_full_name",
        "repo_url",
        "pr_number",
        "pr_url",
        "final_status",
        "created_at",
        "ended_at",
        "review_time_hours",
        "review_count",
        "changed_files",
        "additions",
        "deletions",
        "description_char_count",
        "participants_count",
        "comments_count",
    ]

    with path.open("a", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=";")
        for row in rows:
            writer.writerow(
                {
                    "repo_full_name": row.repo_full_name,
                    "repo_url": row.repo_url,
                    "pr_number": row.pr_number,
                    "pr_url": row.pr_url,
                    "final_status": row.final_status,
                    "created_at": row.created_at,
                    "ended_at": row.ended_at,
                    "review_time_hours": row.review_time_hours,
                    "review_count": row.review_count,
                    "changed_files": row.changed_files,
                    "additions": row.additions,
                    "deletions": row.deletions,
                    "description_char_count": row.description_char_count,
                    "participants_count": row.participants_count,
                    "comments_count": row.comments_count,
                }
            )

    return len(rows)


def load_completed_repositories(path: Path) -> set[str]:
    if not path.exists():
        return set()

    completed: set[str] = set()
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        for row in reader:
            repo_full_name = (row.get("repo_full_name") or "").strip()
            if repo_full_name:
                completed.add(repo_full_name)
    return completed


def append_failed_repo(path: Path, repo_full_name: str, reason: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["repo_full_name", "reason"],
            delimiter=";",
        )
        if write_header:
            writer.writeheader()
        writer.writerow({"repo_full_name": repo_full_name, "reason": reason})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lab03 Sprint1: seleção de repositórios e coleta de métricas de PRs"
    )
    parser.add_argument(
        "--target-repos",
        type=int,
        default=200,
        help="Quantidade alvo de repositórios populares elegíveis (padrão: 200).",
    )
    parser.add_argument(
        "--min-prs",
        type=int,
        default=100,
        help="Quantidade mínima de PRs (MERGED + CLOSED) para o repositório ser elegível.",
    )
    parser.add_argument(
        "--pr-page-size",
        type=int,
        default=50,
        help="Tamanho da página na coleta de PRs por repositório (máx recomendado: 100).",
    )
    parser.add_argument(
        "--max-prs-per-repo",
        type=int,
        default=0,
        help="Limite de PRs elegíveis por repositório. Use 0 para coletar todos.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        help="Pausa (segundos) entre páginas de PR. Padrão 0 para coleta mais rápida.",
    )
    parser.add_argument(
        "--refresh-repos",
        action="store_true",
        help="Força nova seleção de repositórios, ignorando repos_selected.csv.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Retoma coleta a partir de prs_sprint1.csv, pulando repositórios já coletados.",
    )
    return parser.parse_args()


def main() -> None:
    if not os.getenv("GITHUB_TOKEN"):
        raise RuntimeError(f"GITHUB_TOKEN não encontrado. Configure {ENV_PATH}")

    args = parse_args()
    target_repos = max(1, args.target_repos)
    min_prs = max(1, args.min_prs)
    pr_page_size = max(1, min(args.pr_page_size, 100))
    max_prs_per_repo = max(0, args.max_prs_per_repo)

    print("[step] selecionando repositórios...")
    if not args.refresh_repos and SELECTED_REPOS_CSV.exists():
        repos = load_selected_repos_csv(SELECTED_REPOS_CSV)
        if len(repos) >= target_repos:
            repos = repos[:target_repos]
            print(f"[info] reutilizando seleção existente: {SELECTED_REPOS_CSV}")
        else:
            repos = fetch_selected_repositories(target=target_repos, min_prs=min_prs)
            save_selected_repos_csv(repos, SELECTED_REPOS_CSV)
    else:
        repos = fetch_selected_repositories(target=target_repos, min_prs=min_prs)
        save_selected_repos_csv(repos, SELECTED_REPOS_CSV)

    print(f"[info] repositórios selecionados: {len(repos)}")

    print("[step] coletando PRs e métricas...")
    completed_repos = load_completed_repositories(PRS_DATASET_CSV) if args.resume else set()
    if args.resume and completed_repos:
        print(f"[info] retomando coleta; repositórios já processados: {len(completed_repos)}")

    total_rows = 0
    failed_repos = 0
    for idx, repo in enumerate(repos, start=1):
        if repo.full_name in completed_repos:
            print(f"[prs] ({idx}/{len(repos)}) {repo.full_name} - pulado (já coletado)")
            continue

        print(f"[prs] ({idx}/{len(repos)}) {repo.full_name}")
        try:
            repo_rows = fetch_repository_prs(
                repo,
                page_size=pr_page_size,
                max_prs_per_repo=max_prs_per_repo,
                sleep_between_pages=max(0.0, args.sleep),
            )
        except Exception as ex:
            failed_repos += 1
            append_failed_repo(FAILED_REPOS_CSV, repo.full_name, str(ex))
            print(f"[warn] erro em {repo.full_name}: {ex}")
            print("[warn] pulando imediatamente para o próximo repositório.")
            if args.resume:
                completed_repos.add(repo.full_name)
            continue

        if not repo_rows:
            failed_repos += 1
            append_failed_repo(FAILED_REPOS_CSV, repo.full_name, "no_eligible_rows_or_partial_failure")

        written = append_pr_dataset_rows(repo_rows, PRS_DATASET_CSV)
        total_rows += written

        if args.resume:
            completed_repos.add(repo.full_name)

    if not PRS_DATASET_CSV.exists():
        save_pr_dataset_csv([], PRS_DATASET_CSV)

    print("\nSPRINT 1 concluída com sucesso.")
    print(f"- Repositórios selecionados: {SELECTED_REPOS_CSV}")
    print(f"- Dataset de PRs:            {PRS_DATASET_CSV}")
    print(f"- PRs elegíveis coletados:   {total_rows}")
    print(f"- Repositórios com alerta:   {failed_repos}")
    print(f"- Log de alertas:            {FAILED_REPOS_CSV}")


if __name__ == "__main__":
    main()
