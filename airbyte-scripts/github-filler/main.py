import sys
from github import GitHubFiller

if __name__ == "__main__":
    api_token = sys.argv[1]
    repository = sys.argv[2]
    executor = GitHubFiller(api_token, repository)
    executor.run()
