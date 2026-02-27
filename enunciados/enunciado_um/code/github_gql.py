from __future__ import annotations

import os
import time
import random
import requests

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

class GitHubGraphQLError(RuntimeError):
    pass

def graphql_request(query: str, variables: dict | None = None, *, max_retries: int = 10) -> dict:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN não encontrado. Verifique o .env / ambiente.")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "lab01S01-pucminas",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {"query": query, "variables": variables or {}}

    session = requests.Session()
    session.trust_env = False  # <- evita proxy do ambiente

    last_status = None
    last_text = None

    for attempt in range(1, max_retries + 1):
        try:
            resp = session.post(
                GITHUB_GRAPHQL_URL,
                json=payload,
                headers=headers,
                timeout=(10, 60),
            )

            last_status = resp.status_code
            last_text = resp.text

            # 429 = rate limit; 502/503/504 = instabilidade/proxy/edge
            if resp.status_code in (429, 502, 503, 504):
                # Log leve (uma linha)
                print(f"[retry] tentativa {attempt}/{max_retries} -> HTTP {resp.status_code}")

                if attempt == max_retries:
                    raise GitHubGraphQLError(f"HTTP {resp.status_code}: {resp.text}")

                # Backoff exponencial com jitter
                sleep_s = min(2 ** (attempt - 1), 20) + random.random()
                time.sleep(sleep_s)
                continue

            resp.raise_for_status()

            data = resp.json()
            if "errors" in data and data["errors"]:
                raise GitHubGraphQLError(str(data["errors"]))

            return data

        except (requests.Timeout, requests.ConnectionError) as e:
            print(f"[retry] tentativa {attempt}/{max_retries} -> erro de rede: {e}")
            if attempt == max_retries:
                raise GitHubGraphQLError(f"Erro de rede após {max_retries} tentativas: {e}") from e
            sleep_s = min(2 ** (attempt - 1), 20) + random.random()
            time.sleep(sleep_s)

    raise GitHubGraphQLError(f"Falha inesperada. Último HTTP={last_status} body={last_text}")