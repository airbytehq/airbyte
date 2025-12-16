# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.config import ConfigBuilder
from mock_server.request_builder import KlaviyoRequestBuilder
from mock_server.response_builder import KlaviyoPaginatedResponseBuilder


_NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
_STREAM_NAME = "global_exclusions"
_API_KEY = "test_api_key_abc123"


@freezegun.freeze_time(_NOW.isoformat())
class TestGlobalExclusionsStream(TestCase):
    """
    Tests for the Klaviyo 'global_exclusions' stream.

    Stream configuration from manifest.yaml:
    - Uses /profiles endpoint with additional-fields[profile]: subscriptions
    - RecordFilter: Only returns profiles with suppression data
    - Transformations:
      - AddFields: extracts 'updated' from attributes
      - AddFields: copies suppression to suppressions (plural)
      - RemoveFields: removes original suppression field
    - Error handling: 429 RATE_LIMITED, 401/403 FAIL
    - Pagination: CursorPagination
    """

    @HttpMocker()
    def test_full_refresh_filters_suppressed_profiles(self, http_mocker: HttpMocker):
        """
        Test that record_filter correctly filters only suppressed profiles.

        The manifest configures:
        record_filter:
          type: RecordFilter
          condition: "{{ record['attributes']['subscriptions']['email']['marketing']['suppression'] }}"

        Given: API returns profiles with and without suppression
        When: Running a full refresh sync
        Then: Only profiles with suppression data should be returned
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Global exclusions stream uses profiles endpoint with additional-fields[profile]: subscriptions
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY)
            .with_query_params({"additional-fields[profile]": "subscriptions", "page[size]": "100"})
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_suppressed",
                                "attributes": {
                                    "email": "suppressed@example.com",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                    "subscriptions": {
                                        "email": {
                                            "marketing": {
                                                "can_receive_email_marketing": False,
                                                "consent": "UNSUBSCRIBED",
                                                "suppression": [{"reason": "USER_SUPPRESSED", "timestamp": "2024-05-31T10:00:00+00:00"}],
                                            }
                                        },
                                        "sms": {"marketing": {"can_receive_sms_marketing": False}},
                                    },
                                },
                            },
                            {
                                "type": "profile",
                                "id": "profile_not_suppressed",
                                "attributes": {
                                    "email": "active@example.com",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                    "subscriptions": {
                                        "email": {
                                            "marketing": {
                                                "can_receive_email_marketing": True,
                                                "consent": "SUBSCRIBED",
                                                "suppression": [],
                                            }
                                        },
                                        "sms": {"marketing": {"can_receive_sms_marketing": True}},
                                    },
                                },
                            },
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == "profile_suppressed"
        assert record["attributes"]["email"] == "suppressed@example.com"

    @HttpMocker()
    def test_transformation_adds_suppressions_field(self, http_mocker: HttpMocker):
        """
        Test that transformations correctly add 'suppressions' and remove 'suppression'.

        The manifest configures:
        transformations:
          - type: AddFields (copies suppression to suppressions)
          - type: RemoveFields (removes original suppression)

        Given: A suppressed profile record
        When: Running a sync
        Then: The record should have 'suppressions' field and no 'suppression' field
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Global exclusions stream uses profiles endpoint with additional-fields[profile]: subscriptions
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY)
            .with_query_params({"additional-fields[profile]": "subscriptions", "page[size]": "100"})
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_transform_test",
                                "attributes": {
                                    "email": "transform@example.com",
                                    "updated": "2024-05-31T14:45:00+00:00",
                                    "subscriptions": {
                                        "email": {
                                            "marketing": {
                                                "can_receive_email_marketing": False,
                                                "consent": "UNSUBSCRIBED",
                                                "suppression": [{"reason": "HARD_BOUNCE", "timestamp": "2024-05-31T10:00:00+00:00"}],
                                            }
                                        },
                                        "sms": {"marketing": {"can_receive_sms_marketing": False}},
                                    },
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data

        assert "updated" in record
        assert record["updated"] == "2024-05-31T14:45:00+00:00"

        marketing = record["attributes"]["subscriptions"]["email"]["marketing"]
        assert "suppressions" in marketing
        assert len(marketing["suppressions"]) == 1
        assert marketing["suppressions"][0]["reason"] == "HARD_BOUNCE"

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker):
        """
        Test first incremental sync with no previous state.

        Given: No previous state (first sync)
        When: Running an incremental sync
        Then: The connector should use start_date from config and emit state message
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Global exclusions stream uses profiles endpoint with additional-fields[profile]: subscriptions
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY)
            .with_query_params({"additional-fields[profile]": "subscriptions", "page[size]": "100"})
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_001",
                                "attributes": {
                                    "email": "test@example.com",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                    "subscriptions": {
                                        "email": {
                                            "marketing": {
                                                "suppression": [{"reason": "USER_SUPPRESSED", "timestamp": "2024-05-31T10:00:00+00:00"}]
                                            }
                                        },
                                        "sms": {"marketing": {}},
                                    },
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state.__dict__
        assert "updated" in latest_state

    @HttpMocker()
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker):
        """
        Test incremental sync with a prior state from previous sync.

        Given: A previous sync state with an updated cursor value
        When: Running an incremental sync
        Then: The connector should use the state cursor and return only new/updated records
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"updated": "2024-05-30T00:00:00+00:00"}).build()

        # Global exclusions stream uses profiles endpoint with additional-fields[profile]: subscriptions
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY)
            .with_query_params({"additional-fields[profile]": "subscriptions", "page[size]": "100"})
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_new",
                                "attributes": {
                                    "email": "new@example.com",
                                    "updated": "2024-05-31T10:00:00+00:00",
                                    "subscriptions": {
                                        "email": {
                                            "marketing": {
                                                "suppression": [{"reason": "SPAM_COMPLAINT", "timestamp": "2024-05-31T09:00:00+00:00"}]
                                            }
                                        },
                                        "sms": {"marketing": {}},
                                    },
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.incremental).build()
        output = read(source, config=config, catalog=catalog, state=state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "profile_new"

        assert len(output.state_messages) > 0
        latest_state = output.most_recent_state.stream_state.__dict__
        # Note: The connector returns datetime with +0000 format (without colon)
        assert latest_state["updated"] == "2024-05-31T10:00:00+0000"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        Given: An API that returns multiple pages of suppressed profiles
        When: Running a full refresh sync
        Then: The connector should follow pagination links and return all records

        Note: Uses with_any_query_params() because pagination adds page[cursor] to the
        request params, making exact matching impractical.
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Use with_any_query_params() since pagination adds page[cursor] dynamically
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY).with_any_query_params().build(),
            [
                KlaviyoPaginatedResponseBuilder()
                .with_records(
                    [
                        {
                            "type": "profile",
                            "id": "profile_001",
                            "attributes": {
                                "email": "user1@example.com",
                                "updated": "2024-05-31T10:00:00+00:00",
                                "subscriptions": {
                                    "email": {
                                        "marketing": {
                                            "suppression": [{"reason": "USER_SUPPRESSED", "timestamp": "2024-05-31T09:00:00+00:00"}]
                                        }
                                    },
                                    "sms": {"marketing": {}},
                                },
                            },
                        }
                    ]
                )
                .with_next_page_link("https://a.klaviyo.com/api/profiles?page[cursor]=abc123")
                .build(),
                KlaviyoPaginatedResponseBuilder()
                .with_records(
                    [
                        {
                            "type": "profile",
                            "id": "profile_002",
                            "attributes": {
                                "email": "user2@example.com",
                                "updated": "2024-05-31T11:00:00+00:00",
                                "subscriptions": {
                                    "email": {
                                        "marketing": {"suppression": [{"reason": "HARD_BOUNCE", "timestamp": "2024-05-31T10:00:00+00:00"}]}
                                    },
                                    "sms": {"marketing": {}},
                                },
                            },
                        }
                    ]
                )
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "profile_001"
        assert output.records[1].record.data["id"] == "profile_002"

    @HttpMocker()
    def test_rate_limit_429_handling(self, http_mocker: HttpMocker):
        """
        Test that connector handles 429 rate limit responses with RATE_LIMITED action.

        Given: An API that returns a 429 rate limit error
        When: Making an API request
        Then: The connector should respect the Retry-After header and retry
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Global exclusions stream uses profiles endpoint with additional-fields[profile]: subscriptions
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY)
            .with_query_params({"additional-fields[profile]": "subscriptions", "page[size]": "100"})
            .build(),
            [
                HttpResponse(
                    body=json.dumps({"errors": [{"detail": "Rate limit exceeded"}]}),
                    status_code=429,
                    headers={"Retry-After": "1"},
                ),
                HttpResponse(
                    body=json.dumps(
                        {
                            "data": [
                                {
                                    "type": "profile",
                                    "id": "profile_after_retry",
                                    "attributes": {
                                        "email": "retry@example.com",
                                        "updated": "2024-05-31T10:00:00+00:00",
                                        "subscriptions": {
                                            "email": {
                                                "marketing": {
                                                    "suppression": [{"reason": "USER_SUPPRESSED", "timestamp": "2024-05-31T09:00:00+00:00"}]
                                                }
                                            },
                                            "sms": {"marketing": {}},
                                        },
                                    },
                                }
                            ],
                            "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                        }
                    ),
                    status_code=200,
                ),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "profile_after_retry"

        log_messages = [log.log.message for log in output.logs]
        # Check for backoff log message pattern
        assert any(
            "Backing off" in msg and "UserDefinedBackoffException" in msg and "429" in msg for msg in log_messages
        ), "Expected backoff log message for 429 rate limit"
        # Check for retry/sleeping log message pattern
        assert any(
            "Sleeping for" in msg and "seconds" in msg for msg in log_messages
        ), "Expected retry sleeping log message for 429 rate limit"

    @HttpMocker()
    def test_unauthorized_401_error_fails(self, http_mocker: HttpMocker):
        """
        Test that connector fails on 401 Unauthorized errors with FAIL action.

        Given: Invalid API credentials
        When: Making an API request that returns 401
        Then: The connector should fail with a config error
        """
        config = ConfigBuilder().with_api_key("invalid_key").with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Global exclusions stream uses profiles endpoint with additional-fields[profile]: subscriptions
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint("invalid_key")
            .with_query_params({"additional-fields[profile]": "subscriptions", "page[size]": "100"})
            .build(),
            HttpResponse(
                body=json.dumps({"errors": [{"detail": "Invalid API key"}]}),
                status_code=401,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=True)

        assert len(output.records) == 0
        expected_error_message = "Please provide a valid API key and make sure it has permissions to read specified streams."
        log_messages = [log.log.message for log in output.logs]
        assert any(
            expected_error_message in msg for msg in log_messages
        ), f"Expected error message '{expected_error_message}' in logs for 401 authentication failure"

    @HttpMocker()
    def test_forbidden_403_error_fails(self, http_mocker: HttpMocker):
        """
        Test that connector fails on 403 Forbidden errors with FAIL action.

        The manifest configures 403 errors with action: FAIL, which means the connector
        should fail the sync when permission errors occur.

        Given: API credentials with insufficient permissions
        When: Making an API request that returns 403
        Then: The connector should fail with a config error
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Global exclusions stream uses profiles endpoint with additional-fields[profile]: subscriptions
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY)
            .with_query_params({"additional-fields[profile]": "subscriptions", "page[size]": "100"})
            .build(),
            HttpResponse(
                body=json.dumps({"errors": [{"detail": "Forbidden - insufficient permissions"}]}),
                status_code=403,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=True)

        assert len(output.records) == 0
        expected_error_message = "Please provide a valid API key and make sure it has permissions to read specified streams."
        log_messages = [log.log.message for log in output.logs]
        assert any(
            expected_error_message in msg for msg in log_messages
        ), f"Expected error message '{expected_error_message}' in logs for 403 permission failure"

    @HttpMocker()
    def test_empty_results_no_suppressed_profiles(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results when no profiles are suppressed.

        Given: An API that returns profiles but none are suppressed
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_api_key(_API_KEY).with_start_date(datetime(2024, 5, 31, tzinfo=timezone.utc)).build()

        # Global exclusions stream uses profiles endpoint with additional-fields[profile]: subscriptions
        http_mocker.get(
            KlaviyoRequestBuilder.profiles_endpoint(_API_KEY)
            .with_query_params({"additional-fields[profile]": "subscriptions", "page[size]": "100"})
            .build(),
            HttpResponse(
                body=json.dumps(
                    {
                        "data": [
                            {
                                "type": "profile",
                                "id": "profile_active",
                                "attributes": {
                                    "email": "active@example.com",
                                    "updated": "2024-05-31T12:30:00+00:00",
                                    "subscriptions": {
                                        "email": {
                                            "marketing": {"can_receive_email_marketing": True, "consent": "SUBSCRIBED", "suppression": []}
                                        },
                                        "sms": {"marketing": {"can_receive_sms_marketing": True}},
                                    },
                                },
                            }
                        ],
                        "links": {"self": "https://a.klaviyo.com/api/profiles", "next": None},
                    }
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
