from __future__ import annotations

import os
import random
import time
from pathlib import Path
from typing import Any

import requests

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


class GitHubGraphQLError(RuntimeError):
    """Raised when a GraphQL request fails after retries."""


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


def graphql_request(
    query: str,
    variables: dict[str, Any] | None = None,
    *,
    max_retries: int = 8,
) -> dict[str, Any]:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN não encontrado. Configure o arquivo .env em code/.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "lab03-sprint1-pucminas",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {"query": query, "variables": variables or {}}

    with requests.Session() as session:
        session.trust_env = False

        for attempt in range(1, max_retries + 1):
            try:
                response = session.post(
                    GITHUB_GRAPHQL_URL,
                    json=payload,
                    headers=headers,
                    timeout=(10, 90),
                )

                if response.status_code in (429, 502, 503, 504):
                    if attempt == max_retries:
                        raise GitHubGraphQLError(f"HTTP {response.status_code}: {response.text}")
                    sleep_seconds = min(2 ** (attempt - 1), 20) + random.random()
                    print(
                        f"[retry {attempt}/{max_retries}] HTTP {response.status_code}; "
                        f"aguardando {sleep_seconds:.1f}s"
                    )
                    time.sleep(sleep_seconds)
                    continue

                response.raise_for_status()
                data = response.json()

                if data.get("errors"):
                    raise GitHubGraphQLError(str(data["errors"]))

                return data
            except (requests.Timeout, requests.ConnectionError) as ex:
                if attempt == max_retries:
                    raise GitHubGraphQLError(
                        f"Falha de rede após {max_retries} tentativas: {ex}"
                    ) from ex
                sleep_seconds = min(2 ** (attempt - 1), 20) + random.random()
                print(
                    f"[retry {attempt}/{max_retries}] falha de rede: {ex}; "
                    f"aguardando {sleep_seconds:.1f}s"
                )
                time.sleep(sleep_seconds)

    raise GitHubGraphQLError("Falha inesperada em graphql_request.")
