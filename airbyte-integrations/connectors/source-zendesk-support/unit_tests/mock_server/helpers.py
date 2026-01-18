# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from datetime import timedelta
from typing import Optional

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime

from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    GroupsRecordBuilder,
    GroupsResponseBuilder,
    PostCommentsRecordBuilder,
    PostCommentsResponseBuilder,
    PostsRecordBuilder,
    PostsResponseBuilder,
    TicketFormsRecordBuilder,
    TicketFormsResponseBuilder,
    TicketsRecordBuilder,
    TicketsResponseBuilder,
)
from .utils import datetime_to_string


def given_ticket_forms(
    http_mocker: HttpMocker, start_date: AirbyteDateTime, api_token_authenticator: ApiTokenAuthenticator
) -> TicketFormsRecordBuilder:
    """
    Ticket Forms reqests
    """
    ticket_forms_record_builder = TicketFormsRecordBuilder.ticket_forms_record().with_field(
        FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(seconds=1)))
    )
    http_mocker.get(
        ZendeskSupportRequestBuilder.ticket_forms_endpoint(api_token_authenticator).build(),
        TicketFormsResponseBuilder.ticket_forms_response().with_record(ticket_forms_record_builder).build(),
    )
    return ticket_forms_record_builder


def given_posts(
    http_mocker: HttpMocker,
    start_date: AirbyteDateTime,
    api_token_authenticator: ApiTokenAuthenticator,
    updated_at: Optional[AirbyteDateTime] = None,
) -> PostsRecordBuilder:
    """
    Posts requests setup
    """
    posts_record_builder = PostsRecordBuilder.posts_record().with_field(
        FieldPath("updated_at"), datetime_to_string(updated_at if updated_at else start_date.add(timedelta(seconds=1)))
    )
    http_mocker.get(
        ZendeskSupportRequestBuilder.posts_endpoint(api_token_authenticator)
        .with_start_time(datetime_to_string(start_date))
        .with_page_size(100)
        .build(),
        PostsResponseBuilder.posts_response().with_record(posts_record_builder).build(),
    )
    return posts_record_builder


def given_posts_multiple(
    http_mocker: HttpMocker,
    start_date: AirbyteDateTime,
    api_token_authenticator: ApiTokenAuthenticator,
    updated_at: Optional[AirbyteDateTime] = None,
) -> tuple:
    """
    Posts requests setup with 2 parent records (per playbook requirement for substream tests).
    Returns a tuple of (post1_record_builder, post2_record_builder).
    """
    posts_record_builder_1 = (
        PostsRecordBuilder.posts_record()
        .with_id(1001)
        .with_field(FieldPath("updated_at"), datetime_to_string(updated_at if updated_at else start_date.add(timedelta(seconds=1))))
    )
    posts_record_builder_2 = (
        PostsRecordBuilder.posts_record()
        .with_id(1002)
        .with_field(FieldPath("updated_at"), datetime_to_string(updated_at if updated_at else start_date.add(timedelta(seconds=2))))
    )
    http_mocker.get(
        ZendeskSupportRequestBuilder.posts_endpoint(api_token_authenticator)
        .with_start_time(datetime_to_string(start_date))
        .with_page_size(100)
        .build(),
        PostsResponseBuilder.posts_response().with_record(posts_record_builder_1).with_record(posts_record_builder_2).build(),
    )
    return (posts_record_builder_1, posts_record_builder_2)


def given_post_comments(
    http_mocker: HttpMocker,
    start_date: AirbyteDateTime,
    post_id: int,
    api_token_authenticator: ApiTokenAuthenticator,
    updated_at: Optional[AirbyteDateTime] = None,
) -> PostCommentsRecordBuilder:
    """
    Post Comments requests setup
    """
    post_comments_record_builder = PostCommentsRecordBuilder.post_comments_record().with_field(
        FieldPath("updated_at"), datetime_to_string(updated_at if updated_at else start_date.add(timedelta(seconds=1)))
    )
    http_mocker.get(
        ZendeskSupportRequestBuilder.post_comments_endpoint(api_token_authenticator, post_id)
        .with_start_time(datetime_to_string(start_date))
        .with_page_size(100)
        .build(),
        PostCommentsResponseBuilder.post_comments_response().with_record(post_comments_record_builder).build(),
    )
    return post_comments_record_builder


def given_tickets(
    http_mocker: HttpMocker, start_date: AirbyteDateTime, api_token_authenticator: ApiTokenAuthenticator
) -> TicketsRecordBuilder:
    """
    Tickets requests setup
    """
    tickets_record_builder = TicketsRecordBuilder.tickets_record().with_field(FieldPath("generated_timestamp"), start_date.int_timestamp)
    http_mocker.get(
        ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(start_date.int_timestamp).build(),
        TicketsResponseBuilder.tickets_response().with_record(tickets_record_builder).build(),
    )
    return tickets_record_builder


def given_tickets_with_state(
    http_mocker: HttpMocker, start_date: AirbyteDateTime, cursor_value: AirbyteDateTime, api_token_authenticator: ApiTokenAuthenticator
) -> TicketsRecordBuilder:
    """
    Tickets requests setup
    """
    tickets_record_builder = TicketsRecordBuilder.tickets_record().with_cursor(int(cursor_value.timestamp()))
    http_mocker.get(
        ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(int(start_date.timestamp())).build(),
        TicketsResponseBuilder.tickets_response().with_record(tickets_record_builder).build(),
    )
    return tickets_record_builder


def given_groups_with_later_records(
    http_mocker: HttpMocker,
    updated_at_value: AirbyteDateTime,
    later_record_time_delta: timedelta,
    api_token_authenticator: ApiTokenAuthenticator,
) -> GroupsRecordBuilder:
    """
    Creates two group records one with a specific cursor value and one that has a later cursor value based on the
    provided timedelta. This is intended to create multiple records with different times which can be used to
    test functionality like semi-incremental record filtering
    """
    groups_record_builder = GroupsRecordBuilder.groups_record().with_field(FieldPath("updated_at"), datetime_to_string(updated_at_value))

    later_groups_record_builder = GroupsRecordBuilder.groups_record().with_field(
        FieldPath("updated_at"), datetime_to_string(updated_at_value + later_record_time_delta)
    )
    http_mocker.get(
        ZendeskSupportRequestBuilder.groups_endpoint(api_token_authenticator).with_per_page(100).build(),
        GroupsResponseBuilder.groups_response().with_record(groups_record_builder).with_record(later_groups_record_builder).build(),
    )
    return groups_record_builder
