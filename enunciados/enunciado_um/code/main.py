import os

import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

def get_popular_repos(keyword, num_repos) :
    url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc&per_page={num_repos}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else :
        raise Exception("Error to fetch repositories: {response.status_code} - {response.text}")

def get_pull_requests(owner, repo_name) :
    url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else :
        raise Exception("Error to fetch pull requests: {response.status_code} - {response.text}")

def get_releases(owner, repo_name) :
    url = f"https://api.github.com/repos/{owner}/{repo_name}/releases"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else :
        raise Exception("Error to fetch releases: {response.status_code} - {response.text}")

def get_closed_issues(owner, repo_name) :
    url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=closed"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else :
        raise Exception("Error to fetch closed issues: {response.status_code} - {response.text}")

def get_repo_details(owner, repo) :
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else :
        raise Exception("Error to fetch repository details: {response.status_code} - {response.text}")

def collect_and_print_repo_info(repos) :
    for repo in repos:
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        repo_details = get_repo_details(owner, repo_name)

        pull_requests = get_pull_requests(owner, repo_name)
        releases = get_releases(owner, repo_name)
        closed_issues = get_closed_issues(owner, repo_name)

        print(f"Repository: {repo_name}")
        print(f"Owner: {owner}")
        print(f"URL: {repo_details['html_url']}")
        print(f"Stars: {repo_details['stargazers_count']}")
        print(f"Forks: {repo_details['forks_count']}")
        print(f"Created at: {repo_details['created_at']}")
        print(f"Updated at: {repo_details['updated_at']}")
        print(f"Size: {repo_details['size']}")
        print(f"Language: {repo_details['language']}")
        print(f"Open Issues: {repo_details['open_issues_count']}")
        print(f"Watchers: {repo_details['subscribers_count']}")
        print(f"Description: {repo_details['description']}")
        print(f"Pull Requests: {len(pull_requests)}")
        print(f"Releases: {len(releases)}")
        print(f"Closed Issues: {len(closed_issues)}")
        print(f"Topics: {', '.join(repo_details['topics']) if 'topics' in repo_details else 'No topics'}")
        print("=" * 200)

if __name__ == "__main__":
    keyword = input("Enter a keyword to search for repositories: ")
    num_repos = int(input("Enter the number of repositories to retrieve: "))

    try:
        repos_response = get_popular_repos(keyword, num_repos)
        repos = repos_response.get("items", [])
        collect_and_print_repo_info(repos)
    except Exception as e:
        print(e)

