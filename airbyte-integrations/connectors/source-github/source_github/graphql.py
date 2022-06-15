#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sgqlc.operation

from . import github_schema

_schema = github_schema
_schema_root = _schema.github_schema


def get_query(owner, name, page_size, next_page_token):
    kwargs = {"first": page_size}
    if next_page_token:
        kwargs["after"] = next_page_token

    op = sgqlc.operation.Operation(_schema_root.query_type)
    pull_requests = op.repository(owner=owner, name=name).pull_requests(**kwargs)
    pull_requests.nodes.__fields__(
        id="node_id",
        database_id="id",
        number=True,
        updated_at="updated_at",
        changed_files="changed_files",
        deletions=True,
        additions=True,
        merged=True,
        mergeable=True,
        can_be_rebased="can_be_rebased",
        maintainer_can_modify="maintainer_can_modify",
        merge_state_status="merge_state_status",
    )
    pull_requests.nodes.repository.__fields__(name=True)
    pull_requests.nodes.comments.__fields__(total_count=True)
    pull_requests.nodes.commits.__fields__(total_count=True)
    reviews = pull_requests.nodes.reviews(first=100)
    reviews.total_count()
    reviews.nodes.comments.__fields__(total_count=True)
    pull_requests.nodes.merged_by()
    pull_requests.page_info.__fields__(has_next_page=True, end_cursor=True)
    return str(op)
