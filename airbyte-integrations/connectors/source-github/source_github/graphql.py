#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from sgqlc.operation import Operation
from sgqlc.types import Field, Type, datetime, list_of
from sgqlc.types.relay import Connection, connection_args


class IssueCommentConnection(Type):
    totalCount = int


class PullRequestCommitConnection(Type):
    totalCount = int


class PullRequest(Type):
    id = str
    database_id = int
    number = int
    repository = Field("Repository")
    comments = Field(IssueCommentConnection)
    commits = Field(PullRequestCommitConnection)
    updated_at = datetime.DateTime
    changedFiles = int
    deletions = int
    additions = int
    merged = bool
    canBeRebased = bool
    maintainerCanModify = bool
    mergeStateStatus = str


class PullRequestConnection(Connection):
    nodes = list_of(PullRequest)


class Repository(Type):
    name = str
    pull_requests = Field(PullRequestConnection, args=connection_args())


class Query(Type):
    repository = Field(Repository, args={"owner": str, "name": str})


def get_query(owner, name, page_size, next_page_token):
    op = Operation(Query)

    kwargs = {"first": page_size}
    if next_page_token:
        kwargs["after"] = next_page_token

    pull_requests = op.repository(owner=owner, name=name).pull_requests(**kwargs)
    pull_requests.nodes.id()
    pull_requests.nodes.database_id()
    pull_requests.nodes.number()
    pull_requests.nodes.updated_at()
    pull_requests.nodes.repository()
    pull_requests.nodes.comments()
    pull_requests.nodes.commits()
    pull_requests.nodes.changedFiles()
    pull_requests.nodes.deletions()
    pull_requests.nodes.additions()
    pull_requests.nodes.merged()
    pull_requests.nodes.canBeRebased()
    pull_requests.nodes.maintainerCanModify()
    pull_requests.nodes.mergeStateStatus()
    pull_requests.page_info.__fields__("has_next_page")
    pull_requests.page_info.__fields__(end_cursor=True)
    return str(op)
