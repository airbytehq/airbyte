#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# type: ignore
import json
import logging
from typing import Iterator, Optional

import requests


logging.basicConfig(level=logging.INFO)


def logger(func):
    def wrapper(*args):
        logging.info(f"Function: {func.__name__}")
        responses = func(*args)
        for response in responses:
            # github return 3 success status code 200, 201 and 204, we should check all of them
            logging.info(
                f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201, 204] else response.content}'
            )

    return wrapper


class GitHubFiller:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, repository: str):
        self.token = token
        self.repository = repository
        self.session = requests.Session()
        self.session.headers.update(self.get_headers(self.token))

        self.branches: Optional[list] = None

    @staticmethod
    def get_headers(token: str):
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json application/vnd.github.inertia-preview+json",
        }

    def run(self) -> None:
        self.get_all_branches()
        self.pull_requests()
        self.create_milestone()
        labels = ["important", "bug", "critical"]
        milestone = 1
        assignees = []
        self.create_release()
        self.star_a_repository()
        self.create_projects()
        self.add_issues_with_comments(labels, milestone, assignees)

    @logger
    def get_all_branches(self) -> Iterator:
        url = f"{self.BASE_URL}/repos/{self.repository}/branches"
        response = self.session.get(url=url)
        self.branches = response.json()
        yield response

    @logger
    def pull_requests(self) -> Iterator:
        url = f"{self.BASE_URL}/repos/{self.repository}/pulls"

        for branch in self.branches:
            create_pr_data = {
                "title": f'New PR from {branch.get("name")}',
                "head": branch.get("name"),
                "base": "master",
            }
            # create PR
            response = self.session.post(url=url, data=json.dumps(create_pr_data))
            yield response

            if response.status_code == 200 or 201:
                # create review for PR
                create_review_data = {
                    "body": f'Review commit for branch {branch.get("name")}',
                    "event": "COMMENT",
                }
                review_url = f"{self.BASE_URL}/repos/{self.repository}/pulls/{response.json().get('number')}/reviews"
                response = self.session.post(url=review_url, data=json.dumps(create_review_data))
                yield response

                # create comment for commit
                create_comment_data = {
                    "body": f'comment for {branch.get("commit").get("sha")} branch',
                }
                commit_url = f"https://api.github.com/repos/{self.repository}/commits/{branch.get('commit').get('sha')}/comments"
                response = self.session.post(url=commit_url, data=json.dumps(create_comment_data))
                yield response

    @logger
    def add_issues_with_comments(
        self,
        labels: Optional[list],
        milestone: Optional[list],
        assignees: Optional[list],
    ) -> Iterator:
        url = f"{self.BASE_URL}/repos/{self.repository}/issues"

        for branch in self.branches:
            data = {
                "title": f'Issue for branch {branch.get("name")}',
                "head": branch.get("name"),
                "labels": labels,
                "milestone": milestone,
                "assignees": assignees,
            }

            # add issue
            response = self.session.post(url=url, data=json.dumps(data))
            yield response

            # add issue comment
            comments_url = response.json().get("comments_url")
            response = self.add_issue_comment(comments_url)
            yield response

    def add_issue_comment(self, comments_url: str) -> requests.Response:
        return self.session.post(
            url=comments_url,
            data=json.dumps({"body": f"comment for issues {comments_url}"}),
        )

    @logger
    def create_release(self) -> Iterator:
        url = f"{self.BASE_URL}/repos/{self.repository}/releases"

        for i in range(10):
            data = {"tag_name": f"dev-0.{i}", "name": "{i} global release"}
            response = self.session.post(url=url, data=json.dumps(data))
            yield response

    @logger
    def star_a_repository(self) -> Iterator:
        url = f"{self.BASE_URL}/user/starred/{self.repository}"
        response = self.session.put(url=url)
        yield response

    @logger
    def create_projects(self) -> Iterator:
        url = f"{self.BASE_URL}/repos/{self.repository}/projects"
        for name in ["project_1", "project_2", "project_3"]:
            response = self.session.post(url=url, data=json.dumps({"name": name}))
            yield response

    @logger
    def create_milestone(self) -> Iterator:
        url = f"{self.BASE_URL}/repos/{self.repository}/milestones"
        for title in ["main", "test", "feature"]:
            data = {"title": title}
            response = self.session.post(url=url, data=json.dumps(data))
            yield response
