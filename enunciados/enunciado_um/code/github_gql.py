from __future__ import annotations

import os
import requests


GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


class GitHubGraphQLError(RuntimeError):
    pass


def graphql_request(query: str, variables: dict | None = None) -> dict:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN não encontrado. Defina no ambiente ou em um arquivo .env."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    payload = {"query": query, "variables": variables or {}}

    resp = requests.post(
        GITHUB_GRAPHQL_URL,
        json=payload,
        headers=headers,
        timeout=60,
    )

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise GitHubGraphQLError(f"HTTP {resp.status_code}: {resp.text}") from e

    data = resp.json()

    if "errors" in data and data["errors"]:
        raise GitHubGraphQLError(str(data["errors"]))

    return data