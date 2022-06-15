#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sgqlc.operation

from . import github_schema

_schema = github_schema
_schema_root = _schema.github_schema


def get_query(owner, name, page_size, next_page_token):
    op = sgqlc.operation.Operation(_schema_root.query_type)

    kwargs = {"first": page_size}
    if next_page_token:
        kwargs["after"] = next_page_token

    pull_requests = op.repository(owner=owner, name=name).pull_requests(**kwargs)
    pull_requests.nodes.id()
    pull_requests.nodes.database_id()
    pull_requests.nodes.number()
    pull_requests.nodes.updated_at()
    repository = pull_requests.nodes.repository()
    repository.name()
    comments = pull_requests.nodes.comments()
    comments.total_count()
    commits = pull_requests.nodes.commits()
    commits.total_count()
    reviews = pull_requests.nodes.reviews(first=100)
    reviews.total_count()
    reviews_comments = reviews.nodes.comments()
    reviews_comments.total_count()
    pull_requests.nodes.changed_files()
    pull_requests.nodes.deletions()
    pull_requests.nodes.additions()
    pull_requests.nodes.merged()
    pull_requests.nodes.merged_by()
    pull_requests.nodes.can_be_rebased()
    pull_requests.nodes.maintainer_can_modify()
    pull_requests.nodes.merge_state_status()
    pull_requests.page_info.__fields__("has_next_page")
    pull_requests.page_info.__fields__(end_cursor=True)
    return str(op)
