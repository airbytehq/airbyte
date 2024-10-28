# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from typing import Optional

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from pendulum.datetime import DateTime

from .utils import datetime_to_string
from .zs_requests import PostsCommentsRequestBuilder, PostsRequestBuilder, TicketFormsRequestBuilder, TicketsRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_responses import PostsCommentsResponseBuilder, PostsResponseBuilder, TicketFormsResponseBuilder, TicketsResponseBuilder
from .zs_responses.records import PostsCommentsRecordBuilder, PostsRecordBuilder, TicketFormsRecordBuilder, TicketsRecordBuilder


def given_ticket_forms(
    http_mocker: HttpMocker, start_date: DateTime, api_token_authenticator: ApiTokenAuthenticator
) -> TicketFormsRecordBuilder:
    """
    Ticket Forms reqests
    """
    ticket_forms_record_builder = TicketFormsRecordBuilder.ticket_forms_record().with_field(
        FieldPath("updated_at"), datetime_to_string(start_date.add(seconds=1))
    )
    http_mocker.get(
        TicketFormsRequestBuilder.ticket_forms_endpoint(api_token_authenticator).build(),
        TicketFormsResponseBuilder.ticket_forms_response().with_record(ticket_forms_record_builder).build(),
    )
    return ticket_forms_record_builder


def given_posts(http_mocker: HttpMocker, start_date: DateTime, api_token_authenticator: ApiTokenAuthenticator) -> PostsRecordBuilder:
    """
    Posts requests setup
    """
    posts_record_builder = PostsRecordBuilder.posts_record().with_field(
        FieldPath("updated_at"), datetime_to_string(start_date.add(seconds=1))
    )
    http_mocker.get(
        PostsRequestBuilder.posts_endpoint(api_token_authenticator)
        .with_start_time(datetime_to_string(start_date))
        .with_page_size(100)
        .build(),
        PostsResponseBuilder.posts_response().with_record(posts_record_builder).build(),
    )
    return posts_record_builder


def given_post_comments(
    http_mocker: HttpMocker, start_date: DateTime, post_id: int, api_token_authenticator: ApiTokenAuthenticator
) -> PostsCommentsRecordBuilder:
    """
    Post Comments requests setup
    """
    post_comments_record_builder = PostsCommentsRecordBuilder.posts_commetns_record().with_field(
        FieldPath("updated_at"), datetime_to_string(start_date.add(seconds=1))
    )
    http_mocker.get(
        PostsCommentsRequestBuilder.posts_comments_endpoint(api_token_authenticator, post_id)
        .with_start_time(datetime_to_string(start_date))
        .with_page_size(100)
        .build(),
        PostsCommentsResponseBuilder.posts_comments_response().with_record(post_comments_record_builder).build(),
    )
    return post_comments_record_builder

def given_tickets(http_mocker: HttpMocker, start_date: DateTime, api_token_authenticator: ApiTokenAuthenticator) -> TicketsRecordBuilder:
    """
    Tickets requests setup
    """
    tickets_record_builder = TicketsRecordBuilder.tickets_record().with_field(
        FieldPath("generated_timestamp"), start_date.int_timestamp
    )
    http_mocker.get(
        TicketsRequestBuilder.tickets_endpoint(api_token_authenticator)
        .with_start_time(start_date.int_timestamp)
        .build(),
        TicketsResponseBuilder.tickets_response().with_record(tickets_record_builder).build(),
    )
    return tickets_record_builder

def given_tickets_with_state(http_mocker: HttpMocker, start_date: DateTime, cursor_value: DateTime, api_token_authenticator: ApiTokenAuthenticator) -> TicketsRecordBuilder:
    """
    Tickets requests setup
    """
    tickets_record_builder = TicketsRecordBuilder.tickets_record().with_cursor(cursor_value.int_timestamp)
    http_mocker.get(
        TicketsRequestBuilder.tickets_endpoint(api_token_authenticator)
        .with_start_time(start_date.int_timestamp)
        .build(),
        TicketsResponseBuilder.tickets_response().with_record(tickets_record_builder).build(),
    )
    return tickets_record_builder
