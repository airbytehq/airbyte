#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import heapq
import itertools
from typing import Optional

import sgqlc.operation
from sgqlc.operation import Selector

from . import github_schema

_schema = github_schema
_schema_root = _schema.github_schema


def select_user_fields(user):
    user.__fields__(
        id="node_id",
        database_id="id",
        login=True,
        avatar_url="avatar_url",
        url="html_url",
        is_site_admin="site_admin",
    )


def get_query_pull_requests(owner, name, first, after, direction):
    kwargs = {"first": first, "order_by": {"field": "UPDATED_AT", "direction": direction}}
    if after:
        kwargs["after"] = after

    op = sgqlc.operation.Operation(_schema_root.query_type)
    repository = op.repository(owner=owner, name=name)
    repository.name()
    repository.owner.login()
    pull_requests = repository.pull_requests(**kwargs)
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
    pull_requests.nodes.comments.__fields__(total_count=True)
    pull_requests.nodes.commits.__fields__(total_count=True)
    reviews = pull_requests.nodes.reviews(first=100, __alias__="review_comments")
    reviews.total_count()
    reviews.nodes.comments.__fields__(total_count=True)
    user = pull_requests.nodes.merged_by(__alias__="merged_by").__as__(_schema_root.User)
    select_user_fields(user)
    pull_requests.page_info.__fields__(has_next_page=True, end_cursor=True)
    return str(op)


def get_query_reviews(owner, name, first, after, number=None):
    op = sgqlc.operation.Operation(_schema_root.query_type)
    repository = op.repository(owner=owner, name=name)
    repository.name()
    repository.owner.login()
    if number:
        pull_request = repository.pull_request(number=number)
    else:
        kwargs = {"first": first, "order_by": {"field": "UPDATED_AT", "direction": "ASC"}}
        if after:
            kwargs["after"] = after
        pull_requests = repository.pull_requests(**kwargs)
        pull_requests.page_info.__fields__(has_next_page=True, end_cursor=True)
        pull_request = pull_requests.nodes

    pull_request.__fields__(number=True, url=True)
    kwargs = {"first": first}
    if number and after:
        kwargs["after"] = after
    reviews = pull_request.reviews(**kwargs)
    reviews.page_info.__fields__(has_next_page=True, end_cursor=True)
    reviews.nodes.__fields__(
        id="node_id",
        database_id="id",
        body=True,
        state=True,
        url="html_url",
        author_association="author_association",
        submitted_at="submitted_at",
        created_at="created_at",
        updated_at="updated_at",
    )
    reviews.nodes.commit.oid()
    user = reviews.nodes.author(__alias__="user").__as__(_schema_root.User)
    select_user_fields(user)
    return str(op)


def get_query_issue_reactions(owner, name, first, after, number=None):
    op = sgqlc.operation.Operation(_schema_root.query_type)
    repository = op.repository(owner=owner, name=name)
    repository.name()
    repository.owner.login()
    if number:
        issue = repository.issue(number=number)
    else:
        kwargs = {"first": first}
        if after:
            kwargs["after"] = after
        issues = repository.issues(**kwargs)
        issues.page_info.__fields__(has_next_page=True, end_cursor=True)
        issue = issues.nodes

    issue.__fields__(number=True)
    kwargs = {"first": first}
    if number and after:
        kwargs["after"] = after
    reactions = issue.reactions(**kwargs)
    reactions.page_info.__fields__(has_next_page=True, end_cursor=True)
    reactions.nodes.__fields__(
        id="node_id",
        database_id="id",
        content=True,
        created_at="created_at",
    )
    select_user_fields(reactions.nodes.user())
    return str(op)


class QueryReactions:

    # AVERAGE_REVIEWS - optimal number of reviews to fetch inside every pull request.
    # If we try to fetch too many (up to 100) we will spend too many scores of query cost.
    # https://docs.github.com/en/graphql/overview/resource-limitations#calculating-a-rate-limit-score-before-running-the-call
    # If we query too low we would need to make additional sub-queries to fetch the rest of the reviews inside specific pull request.
    AVERAGE_REVIEWS = 5
    AVERAGE_COMMENTS = 2
    AVERAGE_REACTIONS = 2

    def get_query_root_repository(self, owner: str, name: str, first: int, after: Optional[str] = None):
        """
        Get GraphQL query which allows fetching reactions starting from the repository:
        query {
          repository {
            pull_requests(first: page_size) {
              reviews(first: AVERAGE_REVIEWS) {
                comments(first: AVERAGE_COMMENTS) {
                  reactions(first: AVERAGE_REACTIONS) {
                  }
                }
              }
            }
          }
        }
        """
        op = self._get_operation()
        repository = op.repository(owner=owner, name=name)
        repository.name()
        repository.owner.login()

        kwargs = {"first": first}
        if after:
            kwargs["after"] = after
        pull_requests = repository.pull_requests(**kwargs)
        pull_requests.page_info.__fields__(has_next_page=True, end_cursor=True)
        pull_requests.total_count()
        pull_requests.nodes.id(__alias__="node_id")

        reviews = self._select_reviews(pull_requests.nodes, first=self.AVERAGE_REVIEWS)
        comments = self._select_comments(reviews.nodes, first=self.AVERAGE_COMMENTS)
        self._select_reactions(comments.nodes, first=self.AVERAGE_REACTIONS)
        return str(op)

    def get_query_root_pull_request(self, node_id: str, first: int, after: str):
        """
        Get GraphQL query which allows fetching reactions starting from the pull_request:
        query {
          pull_request {
            reviews(first: AVERAGE_REVIEWS) {
              comments(first: AVERAGE_COMMENTS) {
                reactions(first: AVERAGE_REACTIONS) {
                }
              }
            }
          }
        }
        """
        op = self._get_operation()
        pull_request = op.node(id=node_id).__as__(_schema_root.PullRequest)
        pull_request.id(__alias__="node_id")
        pull_request.repository.name()
        pull_request.repository.owner.login()

        reviews = self._select_reviews(pull_request, first, after)
        comments = self._select_comments(reviews.nodes, first=self.AVERAGE_COMMENTS)
        self._select_reactions(comments.nodes, first=self.AVERAGE_REACTIONS)
        return str(op)

    def get_query_root_review(self, node_id: str, first: int, after: str):
        """
        Get GraphQL query which allows fetching reactions starting from the review:
        query {
          review {
            comments(first: AVERAGE_COMMENTS) {
              reactions(first: AVERAGE_REACTIONS) {
              }
            }
          }
        }
        """
        op = self._get_operation()
        review = op.node(id=node_id).__as__(_schema_root.PullRequestReview)
        review.id(__alias__="node_id")
        review.repository.name()
        review.repository.owner.login()

        comments = self._select_comments(review, first, after)
        self._select_reactions(comments.nodes, first=self.AVERAGE_REACTIONS)
        return str(op)

    def get_query_root_comment(self, node_id: str, first: int, after: str):
        """
        Get GraphQL query which allows fetching reactions starting from the comment:
        query {
          comment {
            reactions(first: AVERAGE_REACTIONS) {
            }
          }
        }
        """
        op = self._get_operation()
        comment = op.node(id=node_id).__as__(_schema_root.PullRequestReviewComment)
        comment.id(__alias__="node_id")
        comment.database_id(__alias__="id")
        comment.repository.name()
        comment.repository.owner.login()
        self._select_reactions(comment, first, after)
        return str(op)

    def _select_reactions(self, comment: Selector, first: int, after: Optional[str] = None):
        kwargs = {"first": first}
        if after:
            kwargs["after"] = after
        reactions = comment.reactions(**kwargs)
        reactions.page_info.__fields__(has_next_page=True, end_cursor=True)
        reactions.total_count()
        reactions.nodes.__fields__(id="node_id", database_id="id", content=True, created_at="created_at")
        select_user_fields(reactions.nodes.user())
        return reactions

    def _select_comments(self, review: Selector, first: int, after: Optional[str] = None):
        kwargs = {"first": first}
        if after:
            kwargs["after"] = after
        comments = review.comments(**kwargs)
        comments.page_info.__fields__(has_next_page=True, end_cursor=True)
        comments.total_count()
        comments.nodes.id(__alias__="node_id")
        comments.nodes.database_id(__alias__="id")
        return comments

    def _select_reviews(self, pull_request: Selector, first: int, after: Optional[str] = None):
        kwargs = {"first": first}
        if after:
            kwargs["after"] = after
        reviews = pull_request.reviews(**kwargs)
        reviews.page_info.__fields__(has_next_page=True, end_cursor=True)
        reviews.total_count()
        reviews.nodes.id(__alias__="node_id")
        reviews.nodes.database_id(__alias__="id")
        return reviews

    def _get_operation(self):
        return sgqlc.operation.Operation(_schema_root.query_type)


class CursorStorage:
    def __init__(self, typenames):
        self.typename_to_prio = {o: prio for prio, o in enumerate(reversed(typenames))}
        self.count = itertools.count()
        self.storage = []

    def add_cursor(self, typename, cursor, total_count, parent_id=None):
        priority = self.typename_to_prio[typename]
        heapq.heappush(self.storage, (priority, next(self.count), (typename, cursor, total_count, parent_id)))

    def get_cursor(self):
        if self.storage:
            _, _, c = heapq.heappop(self.storage)
            return {"typename": c[0], "cursor": c[1], "total_count": c[2], "parent_id": c[3]}
