import json
import logging
import sys
from typing import List, Optional

import requests

logging.basicConfig(level=logging.INFO)


def logger(func):
    def wrapper(*args):
        logging.info(f'Function: {func.__name__}')
        response = func(*args)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')
    return wrapper


def get_headers(token: str):
    return {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json application/vnd.github.inertia-preview+json',
    }


def get_all_branches(rep, head):
    url = f"https://api.github.com/repos/{rep}/branches"
    response = requests.get(url=url, headers=head)
    return response.json()


def pull_requests(rep: str, branches: list, head: dict):
    logging.info('Function: pull_requests')

    url = f"https://api.github.com/repos/{rep}/pulls"

    for branch in branches:
        create_pr_data = {
            'title': f'New PR from {branch.get("name")}',
            'head': branch.get('name'),
            'base': 'master'
        }
        # create PR
        response = requests.post(url=url, data=json.dumps(create_pr_data), headers=head)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')

        # create review for PR
        create_review_data = {
            'body': f'Review commit for branch {branch.get("name")}',
            'event': 'COMMENT',
            }
        review_url = f"https://api.github.com/repos/{rep}/pulls/{response.json().get('number')}/reviews"
        response = requests.post(url=review_url, data=json.dumps(create_review_data), headers=head)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')

        # create comment for commit
        create_comment_data = {
            'body': f'comment for {branch.get("commit").get("sha")} branch',
            }
        commit_url = f"https://api.github.com/repos/{rep}/commits/{branch.get('commit').get('sha')}/comments"
        response = requests.post(url=commit_url, data=json.dumps(create_comment_data), headers=head)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')


def add_issues_with_comments(rep: str, branches: List[dict], head: dict, labels: Optional[list], milestone: Optional[list], assignees: Optional[list]):
    logging.info('Function: add_issues_with_comments')
    url = f"https://api.github.com/repos/{rep}/issues"

    for branch in branches:
        data = {
            'title': f'Issue for branch {branch.get("name")}',
            'head': branch.get('name'),
            'labels': labels,
            'milestone': milestone,
            'assignees': assignees
        }

        # add issue
        response = requests.post(url=url, data=json.dumps(data), headers=head)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')

        # add issue comment
        comments_url = response.json().get('comments_url')
        response = requests.post(url=comments_url, data=json.dumps({'body': f'comment for issues {comments_url}'}), headers=head)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')


def create_release(rep: str, head: dict):
    url = f"https://api.github.com/repos/{rep}/releases"
    for i in range(10):
        data = {
            'tag_name': f'dev-0.{i}',
            'name': '{i} global release'
        }
        response = requests.post(url=url, data=json.dumps(data), headers=head)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')


@logger
def star_a_repository(rep: str, head: dict):
    url = f"https://api.github.com/user/starred/{rep}"
    return requests.put(url=url, headers=head)


def create_project(rep: str, head: dict):
    url = f"https://api.github.com/repos/{rep}/projects"
    for name in ['project_1', 'project_2', 'project_3']:
        response = requests.post(url=url, data=json.dumps({'name': name}), headers=head)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')
    

def create_milestone(rep: str, head: dict):
    url = f"https://api.github.com/repos/{rep}/milestones"
    for title in ['main', 'test', 'feature']:
        data = {
            'title': title
        }
        response = requests.post(url=url, data=json.dumps(data), headers=head)
        logging.info(f'Response status: {response.status_code}, response body: {"Success" if response.status_code in [200, 201] else response.content}')
    

if __name__ == "__main__":

    api_token = sys.argv[1]
    repository = sys.argv[2]

    headers = get_headers(api_token)
    branches = get_all_branches(repository, headers)
    
    pull_requests(repository, branches, headers)
    

    create_milestone(repository, headers)
    labels = ['important', 'bug', 'critical']
    milestone = 1
    assignees = []

    create_release(repository, headers)
    star_a_repository(repository, headers)
    create_project(repository, headers)
    add_issues_with_comments(repository, branches, headers, labels, milestone, assignees)
