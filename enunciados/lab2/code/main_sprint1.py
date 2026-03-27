from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

from github_gql import graphql_request

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "output"
REPOS_DIR = OUTPUT_DIR / "repos"
CK_DIR = OUTPUT_DIR / "ck"
CK_JAR_PATH = CK_DIR / "ck.jar"

load_dotenv(dotenv_path=ENV_PATH, override=False)

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
        nameWithOwner
        url
        stargazerCount
        createdAt
        updatedAt
        defaultBranchRef { name }
      }
    }
  }
}
"""


@dataclass
class Repo:
    name: str
    full_name: str
    url: str
    stars: int
    created_at: str
    updated_at: str
    default_branch: str




def fetch_top_1000_java_repositories(target: int = 1000) -> list[Repo]:
    search_query = "language:Java stars:>0 sort:stars-desc"
    page_size = 100
    cursor: str | None = None
    repos: list[Repo] = []

    while len(repos) < target:
        fetch_n = min(page_size, target - len(repos))
        page_no = len(repos) // page_size + 1
        print(f"[GitHub] página {page_no}: coletando {fetch_n} repositórios...")

        result = graphql_request(
            QUERY_SEARCH_PAGE,
            {"q": search_query, "n": fetch_n, "cursor": cursor},
        )

        search = result["data"]["search"]
        for node in search["nodes"]:
            repos.append(
                Repo(
                    name=node["name"],
                    full_name=node["nameWithOwner"],
                    url=node["url"],
                    stars=int(node["stargazerCount"]),
                    created_at=node["createdAt"],
                    updated_at=node["updatedAt"],
                    default_branch=(node.get("defaultBranchRef") or {}).get("name", "main"),
                )
            )

        if not search["pageInfo"]["hasNextPage"]:
            break

        cursor = search["pageInfo"]["endCursor"]

    return repos[:target]




def clone_repository(repo: Repo, destination_root: Path) -> Path:
    destination_root.mkdir(parents=True, exist_ok=True)
    safe_name = repo.full_name.replace("/", "__")
    repo_path = destination_root / safe_name

    if repo_path.exists():
        print(f"[clone] repositório já existe em {repo_path}, reutilizando.")
        return repo_path

    clone_command = [
        "git",
        "clone",
        "--depth",
        "1",
        repo.url,
        str(repo_path),
    ]
    print(f"[clone] clonando {repo.full_name}...")
    subprocess.run(clone_command, check=True)
    return repo_path


def _fetch_latest_ck_release_jar_url() -> str:
    # Algumas instalações retornam 404 em /releases/latest para este projeto,
    # então tentamos fontes em ordem de prioridade.
    candidate_urls: list[str] = []

    try:
        response = requests.get(
            "https://api.github.com/repos/mauricioaniche/ck/releases/latest",
            timeout=(10, 60),
        )
        if response.ok:
            release_data = response.json()
            for asset in release_data.get("assets", []):
                name = str(asset.get("name", ""))
                if name.endswith("-jar-with-dependencies.jar"):
                    candidate_urls.append(str(asset["browser_download_url"]))
    except requests.RequestException:
        pass

    # Fallback estável no Maven Central.
    candidate_urls.append(
        "https://repo1.maven.org/maven2/com/github/mauricioaniche/ck/0.7.0/ck-0.7.0-jar-with-dependencies.jar"
    )

    for url in candidate_urls:
        try:
            probe = requests.head(url, allow_redirects=True, timeout=(10, 30))
            if probe.ok:
                return url
        except requests.RequestException:
            continue

    raise RuntimeError(
        "Não foi possível localizar um CK jar executável (GitHub Releases/Maven Central)."
    )


def ensure_ck_jar(ck_jar_path: Path) -> Path:
    if ck_jar_path.exists():
        print(f"[CK] jar encontrado: {ck_jar_path}")
        return ck_jar_path

    ck_jar_path.parent.mkdir(parents=True, exist_ok=True)
    jar_url = _fetch_latest_ck_release_jar_url()
    print(f"[CK] baixando jar: {jar_url}")

    with requests.get(jar_url, stream=True, timeout=(10, 120)) as response:
        response.raise_for_status()
        with ck_jar_path.open("wb") as output:
            shutil.copyfileobj(response.raw, output)

    return ck_jar_path


def run_ck_analysis(ck_jar_path: Path, repo_path: Path, output_path: Path) -> Path:
    output_path.mkdir(parents=True, exist_ok=True)
    output_arg = str(output_path) + os.sep

    command = [
        "java",
        "-jar",
        str(ck_jar_path),
        str(repo_path),
        "false",
        "0",
        "false",
        output_arg,
    ]

    print("[CK] executando análise estática...")
    subprocess.run(command, check=True)

    expected = output_path / "class.csv"
    concatenated = output_path.parent / f"{output_path.name}class.csv"

    if expected.exists():
        class_csv = expected
    elif concatenated.exists():
        class_csv = concatenated
    else:
        raise RuntimeError(
            f"CK executou, mas não gerou {expected} (nem {concatenated})"
        )

    return class_csv




def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lab02 Sprint 1: Top 1000 Java + clone + coleta CK de 1 repositório"
    )
    parser.add_argument(
        "--repo-index",
        type=int,
        default=1,
        help="Posição (1-based) do repositório que será clonado e analisado pelo CK.",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=1000,
        help="Quantidade de repositórios Java a coletar (padrão: 1000).",
    )
    return parser.parse_args()


def main() -> None:
    if not os.getenv("GITHUB_TOKEN"):
        raise RuntimeError(f"GITHUB_TOKEN não encontrado. Configure {ENV_PATH}")

    args = parse_arguments()

    target = max(1, min(args.target, 1000))
    repos = fetch_top_1000_java_repositories(target=target)

    repo_index = max(1, min(args.repo_index, len(repos)))
    repo = repos[repo_index - 1]
    print(f"[info] repositório selecionado para coleta de métricas: #{repo_index} {repo.full_name}")

    repo_path = clone_repository(repo, REPOS_DIR)
    ck_jar = ensure_ck_jar(CK_JAR_PATH)

    ck_output_for_repo = OUTPUT_DIR / "ck_metrics" / repo.full_name.replace("/", "__")
    run_ck_analysis(ck_jar, repo_path, ck_output_for_repo)

    print("\nSPRINT 1 concluída com sucesso.")
    print(f"- Saida do CK (1 repo): {ck_output_for_repo}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as ex:
        print(f"Erro ao executar comando externo: {ex}")
        sys.exit(ex.returncode or 1)
    except Exception as ex:
        print(f"Erro: {ex}")
        sys.exit(1)
