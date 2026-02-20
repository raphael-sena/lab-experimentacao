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


if __name__ == "__main__":
    keyword = input("Enter a keyword to search for repositories: ")
    num_repos = int(input("Enter the number of repositories to retrieve: "))

    try:
        repos = get_popular_repos(keyword, num_repos)
        for repo in repos["items"]:
            print(f"Name: {repo['name']}, Stars: {repo['stargazers_count']}, URL: {repo['html_url']}")
    except Exception as e:
        print(e)

