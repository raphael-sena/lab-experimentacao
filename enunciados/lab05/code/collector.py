import os
import time
import random
import csv
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER", "official-stockfish")
REPO_NAME = os.getenv("REPO_NAME", "Stockfish")
NUM_TRIALS = int(os.getenv("NUM_TRIALS", "30"))
DELAY = float(os.getenv("DELAY_BETWEEN_REQUESTS", "1.5"))

# API endpoints configurations
REST_BASE_URL = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"

# Setup directories
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_data.csv")

def get_headers():
    if not GITHUB_TOKEN or GITHUB_TOKEN == "your_personal_access_token_here":
        raise ValueError(
            "GITHUB_TOKEN is missing or not set in the environment or .env file.\n"
            "Please create a GitHub Personal Access Token and add it to your .env file."
        )
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "User-Agent": "GraphQL-vs-REST-Experiment-Client",
        "Accept": "application/vnd.github.v3+json",
        "Cache-Control": "no-cache"
    }

# Defining GraphQL Queries (selecting only fields that correspond to basic list display)
GRAPHQL_QUERIES = {
    "repo": {
        "query": """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            name
            description
            homepageUrl
            forkCount
            stargazerCount
            createdAt
            updatedAt
          }
        }
        """,
        "variables": {"owner": REPO_OWNER, "name": REPO_NAME}
    },
    "commits": {
        "query": """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: 30) {
                    nodes {
                      oid
                      message
                      committedDate
                      author {
                        name
                        email
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """,
        "variables": {"owner": REPO_OWNER, "name": REPO_NAME}
    },
    "issues": {
        "query": """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            issues(first: 30, orderBy: {field: CREATED_AT, direction: DESC}) {
              nodes {
                number
                title
                state
                createdAt
                author {
                  login
                }
              }
            }
          }
        }
        """,
        "variables": {"owner": REPO_OWNER, "name": REPO_NAME}
    },
    "pulls": {
        "query": """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            pullRequests(first: 30, orderBy: {field: CREATED_AT, direction: DESC}) {
              nodes {
                number
                title
                state
                createdAt
                author {
                  login
                }
              }
            }
          }
        }
        """,
        "variables": {"owner": REPO_OWNER, "name": REPO_NAME}
    }
}

# REST API Paths
REST_PATHS = {
    "repo": f"/repos/{REPO_OWNER}/{REPO_NAME}",
    "commits": f"/repos/{REPO_OWNER}/{REPO_NAME}/commits?per_page=30",
    "issues": f"/repos/{REPO_OWNER}/{REPO_NAME}/issues?per_page=30&state=all",
    "pulls": f"/repos/{REPO_OWNER}/{REPO_NAME}/pulls?per_page=30&state=all"
}

def execute_rest_request(endpoint, headers):
    url = REST_BASE_URL + REST_PATHS[endpoint]
    
    start_time = time.perf_counter()
    response = requests.get(url, headers=headers)
    end_time = time.perf_counter()
    
    latency_ms = (end_time - start_time) * 1000
    size_bytes = len(response.content)
    
    return response.status_code, latency_ms, size_bytes

def execute_graphql_request(endpoint, headers):
    payload = GRAPHQL_QUERIES[endpoint]
    
    start_time = time.perf_counter()
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    end_time = time.perf_counter()
    
    latency_ms = (end_time - start_time) * 1000
    size_bytes = len(response.content)
    
    # Check if there are GraphQL-specific errors in the JSON response
    status_code = response.status_code
    if status_code == 200:
        res_json = response.json()
        if "errors" in res_json:
            # Indicate GraphQL internal error (e.g. bad query or permissions)
            status_code = 400
            
    return status_code, latency_ms, size_bytes

def run_experiment():
    print("=" * 60)
    print("      GraphQL vs REST Controlled Experiment Data Collector")
    print("=" * 60)
    print(f"Target repository: {REPO_OWNER}/{REPO_NAME}")
    print(f"Number of trials per combination: {NUM_TRIALS}")
    print(f"Inter-request delay: {DELAY}s")
    print(f"Output destination: {RAW_DATA_PATH}")
    print("-" * 60)
    
    try:
        headers = get_headers()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nPlease configure your .env file or environment variables before running.")
        return

    # Build the task list
    # We run 'repo', 'commits', 'issues', 'pulls' for both REST and GraphQL, NUM_TRIALS times each.
    tasks = []
    for trial in range(1, NUM_TRIALS + 1):
        for api_type in ["REST", "GraphQL"]:
            for endpoint in ["repo", "commits", "issues", "pulls"]:
                tasks.append({
                    "trial": trial,
                    "api_type": api_type,
                    "endpoint": endpoint
                })
                
    # Randomize the execution order to eliminate temporal/caching confounders
    random.shuffle(tasks)
    total_tasks = len(tasks)
    print(f"Prepared {total_tasks} API calls to make in a randomized, interleaved order.")
    
    # Write CSV Header if file doesn't exist, otherwise append
    file_exists = os.path.exists(RAW_DATA_PATH)
    with open(RAW_DATA_PATH, mode="a" if file_exists else "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["timestamp", "trial", "api_type", "endpoint", "latency_ms", "size_bytes", "status_code"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            
        success_count = 0
        error_count = 0
        
        for idx, task in enumerate(tasks, start=1):
            trial = task["trial"]
            api_type = task["api_type"]
            endpoint = task["endpoint"]
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            print(f"[{idx}/{total_tasks}] Trial {trial:02d} | Executing {api_type:7s} request for '{endpoint}'... ", end="", flush=True)
            
            try:
                if api_type == "REST":
                    status_code, latency, size = execute_rest_request(endpoint, headers)
                else:
                    status_code, latency, size = execute_graphql_request(endpoint, headers)
                
                if status_code in [200, 201]:
                    writer.writerow({
                        "timestamp": timestamp,
                        "trial": trial,
                        "api_type": api_type,
                        "endpoint": endpoint,
                        "latency_ms": round(latency, 2),
                        "size_bytes": size,
                        "status_code": status_code
                    })
                    csv_file.flush() # Ensure it writes to disk immediately
                    success_count += 1
                    print(f"SUCCESS (status={status_code}, time={latency:.1f}ms, size={size} bytes)")
                else:
                    error_count += 1
                    print(f"FAILED (status={status_code})")
                    
            except Exception as e:
                error_count += 1
                print(f"ERROR: {e}")
            
            # Wait for next call to prevent rate limiting
            if idx < total_tasks:
                time.sleep(DELAY)
                
    print("-" * 60)
    print("Data collection completed!")
    print(f"Total Successful requests written: {success_count}")
    print(f"Total Failed requests: {error_count}")
    print(f"Raw data saved to: {RAW_DATA_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    run_experiment()
