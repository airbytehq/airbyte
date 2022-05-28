#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

# type: ignore
# this is just a script that doesn't need mypy linting
import sys

from github import GitHubFiller

if __name__ == "__main__":
    api_token = sys.argv[1]
    repository = sys.argv[2]
    executor = GitHubFiller(api_token, repository)
    executor.run()
