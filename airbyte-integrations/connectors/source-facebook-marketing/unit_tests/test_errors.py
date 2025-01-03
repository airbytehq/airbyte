#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from facebook_business.exceptions import FacebookRequestError
from source_facebook_marketing.api import API
from source_facebook_marketing.streams import AdAccount, AdCreatives, AdsInsights
from source_facebook_marketing.streams.common import traced_exception

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


FB_API_VERSION = FacebookAdsApi.API_VERSION

account_id = "unknown_account"
some_config = {
    "start_date": "2021-01-23T00:00:00Z",
    "account_ids": [account_id],
    "access_token": "unknown_token",
}
base_url = f"{FacebookSession.GRAPH}/{FB_API_VERSION}/"
act_url = f"{base_url}act_{account_id}/"

ad_account_response = {
    "json": {
        "data": [{"account_id": account_id, "id": f"act_{account_id}"}],
        "status_code": 200,
    }
}
ad_creative_data = [
    {
        "account_id": account_id,
        "id": "111111",
        "name": "ad creative 1",
        "updated_time": "2023-03-21T22:33:56-0700",
    },
    {
        "account_id": account_id,
        "id": "222222",
        "name": "ad creative 2",
        "updated_time": "2023-03-22T22:33:56-0700",
    },
]
ad_creative_response = {
    "json": {
        "data": ad_creative_data,
        "status_code": 200,
    }
}

#     "name, friendly_msg, config_error_response",
CONFIG_ERRORS = [
    (
        "error_400_validating_access_token_session_expired",
        "Invalid access token. Re-authenticate if FB oauth is used or refresh access token with all required permissions",
        {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "Error validating access token: Session has expired on Friday, 18-Aug",
                    "type": "OAuthException",
                    "code": 190,
                    "error_subcode": 463,
                }
            },
        },
    ),
    (
        "error_400_validating_access_token_user_changed_their_password",
        "Invalid access token. Re-authenticate if FB oauth is used or refresh access token with all required permissions",
        {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "Error validating access token: The session has been invalidated because the user changed their password or Facebook has changed the session for security reasons",
                    "type": "OAuthException",
                    "code": 190,
                    "error_subcode": 460,
                }
            },
        },
    ),
    (
        "error_400_validating_access_token_not_authorized_application",
        "Invalid access token. Re-authenticate if FB oauth is used or refresh access token with all required permissions",
        {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "Error validating access token: The user has not authorized application 2586347315015828.",
                    "type": "OAuthException",
                    "code": 190,
                    "error_subcode": 458,
                    "fbtrace_id": "A3pz5DCfhBg3mGCS6Z9z9zY",
                }
            },
        },
    ),
    (
        "error_400_missing_permission",
        "Credentials don't have enough permissions. Check if correct Ad Account Id is used (as in Ads Manager), re-authenticate if FB oauth is used or refresh access token with all required permissions",
        {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "(#100) Missing permissions",
                    "type": "OAuthException",
                    "code": 100,
                }
            },
        },
        # Error randomly happens for different connections.
        # Can be reproduced on https://developers.facebook.com/tools/explorer/?method=GET&path=act_<ad_account_id>&version=v17.0
        # 1st reason: incorrect ad account id is used
        # 2nd reason: access_token does not have permissions:
        #      remove all permissions
        #      re-generate access token
        # Re-authenticate (for cloud) or refresh access token (for oss) and check if all required permissions are granted
    ),
    (
        # One of possible reasons why this error happen is an attempt to access `owner` field:
        #   GET /act_<account-id>?fields=<field-1>,owner,...<field-n>
        "error_403_requires_permission",
        "Credentials don't have enough permissions. Re-authenticate if FB oauth is used or refresh access token with all required permissions.",
        {
            "status_code": 403,
            "json": {
                "error": {
                    "code": 200,
                    "message": "(#200) Requires business_management permission to manage the object",
                }
            },
        },
    ),
    (
        "error_400_permission_must_be_granted",
        "Credentials don't have enough permissions. Re-authenticate if FB oauth is used or refresh access token with all required permissions.",
        {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "Any of the pages_read_engagement, pages_manage_metadata,\n        pages_read_user_content, pages_manage_ads, pages_show_list or\n        pages_messaging permission(s) must be granted before impersonating a\n        user's page.",
                    "type": "OAuthException",
                    "code": 190,
                }
            },
        },
    ),
    (
        "error_unsupported_get_request",
        "Credentials don't have enough permissions. Re-authenticate if FB oauth is used or refresh access token with all required permissions.",
        {
            "json": {
                "error": {
                    "message": "Unsupported get request. Object with ID 'xxx' does not exist, cannot be loaded due to missing permissions, or does not support this operation. Please read the Graph API documentation at https://developers.facebook.com/docs/graph-api",
                    "type": "GraphMethodException",
                    "code": 100,
                    "error_subcode": 33,
                    "fbtrace_id": "A7qVRrTcBm8Pt6iUvnBrxwf",
                }
            },
            "status_code": 400,
        },
    ),
    (
        "error_400_unknown_profile_is_no_linked",
        "Current profile is not linked to delegate page. Check if correct business (not personal) Ad Account Id is used (as in Ads Manager), re-authenticate if FB oauth is used or refresh access token with all required permissions.",
        {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "An unknown error occurred",
                    "type": "OAuthException",
                    "code": 1,
                    "error_subcode": 2853001,
                    "is_transient": False,
                    "error_user_title": "profile is not linked to delegate page",
                    "error_user_msg": "profile should always be linked to delegate page",
                }
            },
        },
        # Error happens on Video stream: https://graph.facebook.com/v17.0/act_XXXXXXXXXXXXXXXX/advideos
        # Recommendations says that the problem can be fixed by switching to Business Ad Account Id
    ),
    (
        "error_400_unknown_profile_is_no_linked_es",
        "Current profile is not linked to delegate page. Check if correct business (not personal) Ad Account Id is used (as in Ads Manager), re-authenticate if FB oauth is used or refresh access token with all required permissions.",
        {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "An unknown error occurred",
                    "type": "OAuthException",
                    "code": 1,
                    "error_subcode": 2853001,
                    "is_transient": False,
                    "error_user_title": "el perfil no est\u00e1 vinculado a la p\u00e1gina del delegado",
                    "error_user_msg": "el perfil deber\u00eda estar siempre vinculado a la p\u00e1gina del delegado",
                }
            },
        },
    ),
    (
        "error_400_start_date_not_within_three_years",
        "Please set the start date of your sync to be within the last 3 years.",
        {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "(#3018) The start date of the time range cannot be beyond 37 months from the current date",
                    "type": "OAuthException",
                    "code": 3018,
                    "fbtrace_id": "Ag-P22y80OSEXM4qsGk2T9P",
                }
            },
        },
    ),
    # ("error_400_unsupported request",
    #  "Re-authenticate because current credential missing permissions",
    #  {
    #      "status_code": 400,
    #      "json": {
    #          "error": {
    #              "message": "Unsupported request - method type: get",
    #              "type": "GraphMethodException",
    #              "code": 100,
    #          }
    #      }
    #  }
    # # for 'ad_account' stream, endpoint: https://graph.facebook.com/v17.0/act_1231630184301950/,
    # # further attempts failed as well
    # # previous sync of 'activities' stream was successfull
    # # It seems like random problem:
    # # - https://stackoverflow.com/questions/71195844/unsupported-request-method-type-get
    # #     "Same issue, but it turned out to be caused by Facebook (confirmed by their employee). A few hours later, the Graph API returned to normal without any action taken."
    # # - https://developers.facebook.com/community/threads/805349521160054/
    # #     "following, I've bein getting this error too, since last week, randomly."
    #
    #
    # # https://developers.facebook.com/community/threads/1232870724022634/
    # # I observed that if I remove preview_shareable_link field from the request, the code is working properly.
    # # Update (Denys Davydov): same for me, but removing the `funding_source_details` field helps, so
    # # we do remove it and do not raise errors; this is tested by a different unit test - see `test_adaccount_list_objects_retry`.
    #
    # ),
]

SERVICE_TEMPORARILY_UNAVAILABLE_TEST_NAME = "error_400_service_temporarily_unavailable"
SERVICE_TEMPORARILY_UNAVAILABLE_RESPONSE = {
    "status_code": 503,
    "json": {
        "error": {
            "message": "(#2) Service temporarily unavailable",
            "type": "OAuthException",
            "is_transient": True,
            "code": 2,
            "fbtrace_id": "AnUyGZoFqN2m50GHVpOQEqr",
        }
    },
}
REDUCE_FIELDS_ERROR_TEST_NAME = "error_500_reduce_the_amount_of_data"
REDUCE_FIELDS_ERROR_RESPONSE = {
    "status_code": 500,
    "json": {
        "error": {
            "message": "Please reduce the amount of data you're asking for, then retry your request",
            "code": 1,
        }
    },
}


class TestRealErrors:
    @pytest.mark.parametrize(
        "name, retryable_error_response",
        [
            (
                "error_400_too_many_calls",
                {
                    "json": {
                        "error": {
                            "message": (
                                "(#80000) There have been too many calls from this ad-account. Wait a bit and try again. "
                                "For more info, please refer to https://developers.facebook.com/docs/graph-api/overview/rate-limiting."
                            ),
                            "type": "OAuthException",
                            "code": 80000,
                            "error_subcode": 2446079,
                            "fbtrace_id": "this_is_fake_response",
                        },
                    },
                    "status_code": 400,
                    "headers": {"x-app-usage": json.dumps({"call_count": 28, "total_time": 25, "total_cputime": 25})},
                },
            ),
            (
                "error_500_unknown",
                {
                    "json": {
                        "error": {
                            "code": 1,
                            "message": "An unknown error occurred",
                            "error_subcode": 99,
                        }
                    },
                    "status_code": 500,
                },
            ),
            (
                SERVICE_TEMPORARILY_UNAVAILABLE_TEST_NAME,
                SERVICE_TEMPORARILY_UNAVAILABLE_RESPONSE,
            ),
            (
                REDUCE_FIELDS_ERROR_TEST_NAME,
                REDUCE_FIELDS_ERROR_RESPONSE,
                # It can be a temporal problem:
                # Happened during 'ad_account' stream sync which always returns only 1 record.
                # Potentially could be caused by some particular field (list of requested fields is constant).
                # But since sync was successful on next attempt, then conclusion is that this is a temporal problem.
            ),
            (
                "error_503_service_unavailable",
                {
                    "json": {
                        "error": {
                            "message": "Call was not successful",
                        }
                    },
                    "status_code": 503,
                },
            ),
        ],
    )
    def test_retryable_error(self, some_config, requests_mock, name, retryable_error_response):
        """Error once, check that we retry and not fail"""
        requests_mock.reset_mock()
        requests_mock.register_uri("GET", f"{act_url}", [retryable_error_response, ad_account_response])
        requests_mock.register_uri(
            "GET",
            f"{act_url}adcreatives",
            [retryable_error_response, ad_creative_response],
        )

        api = API(access_token=some_config["access_token"], page_size=100)
        stream = AdCreatives(api=api, account_ids=some_config["account_ids"])
        ad_creative_records = list(
            stream.read_records(
                sync_mode=SyncMode.full_refresh,
                stream_state={},
                stream_slice={"account_id": account_id},
            )
        )

        assert ad_creative_records == ad_creative_data

    @pytest.mark.parametrize("name, friendly_msg, config_error_response", CONFIG_ERRORS)
    def test_config_error_during_account_info_read(self, requests_mock, name, friendly_msg, config_error_response):
        """Error raised during account info read"""

        api = API(access_token=some_config["access_token"], page_size=100)
        stream = AdCreatives(api=api, account_ids=some_config["account_ids"])

        requests_mock.register_uri("GET", f"{act_url}", [config_error_response, ad_account_response])
        try:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_state={},
                    stream_slice={"account_id": account_id},
                )
            )
            assert False
        except Exception as error:
            assert isinstance(error, AirbyteTracedException)
            assert error.failure_type == FailureType.config_error
            assert friendly_msg in error.message

    @pytest.mark.parametrize("name, friendly_msg, config_error_response", CONFIG_ERRORS)
    def test_config_error_during_actual_nodes_read(self, requests_mock, name, friendly_msg, config_error_response):
        """Error raised during actual nodes read"""

        api = API(access_token=some_config["access_token"], page_size=100)
        stream = AdCreatives(api=api, account_ids=some_config["account_ids"])

        requests_mock.register_uri("GET", f"{act_url}", [ad_account_response])
        requests_mock.register_uri(
            "GET",
            f"{act_url}adcreatives",
            [config_error_response, ad_creative_response],
        )
        try:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_state={},
                    stream_slice={"account_id": account_id},
                )
            )
            assert False
        except Exception as error:
            assert isinstance(error, AirbyteTracedException)
            assert error.failure_type == FailureType.config_error
            assert friendly_msg in error.message

    @pytest.mark.parametrize(
        "name, friendly_msg, config_error_response, failure_type",
        [
            (
                REDUCE_FIELDS_ERROR_TEST_NAME,
                "Please reduce the number of fields requested. Go to the schema tab, "
                "select your source, and unselect the fields you do not need.",
                REDUCE_FIELDS_ERROR_RESPONSE,
                FailureType.config_error,
            ),
            (
                SERVICE_TEMPORARILY_UNAVAILABLE_TEST_NAME,
                "The Facebook API service is temporarily unavailable. This issue should resolve itself, and does not require further action.",
                SERVICE_TEMPORARILY_UNAVAILABLE_RESPONSE,
                FailureType.transient_error,
            ),
        ],
    )
    def test_config_error_that_was_retried_when_reading_nodes(self, requests_mock, name, friendly_msg, config_error_response, failure_type):
        """This test covers errors that have been resolved in the past with a retry strategy, but it could also can fail after retries,
        then, we need to provide the user with a humanized error explaining what just happened"""
        api = API(access_token=some_config["access_token"], page_size=100)
        stream = AdCreatives(api=api, account_ids=some_config["account_ids"])

        requests_mock.register_uri("GET", f"{act_url}", [ad_account_response])
        requests_mock.register_uri(
            "GET",
            f"{act_url}adcreatives",
            [config_error_response],
        )
        try:
            list(
                stream.read_records(
                    sync_mode=SyncMode.full_refresh,
                    stream_state={},
                    stream_slice={"account_id": account_id},
                )
            )
            assert False
        except Exception as error:
            assert isinstance(error, AirbyteTracedException)
            assert error.failure_type == failure_type
            assert (friendly_msg) in error.message

    @pytest.mark.parametrize("name, friendly_msg, config_error_response", CONFIG_ERRORS)
    def test_config_error_insights_account_info_read(self, requests_mock, name, friendly_msg, config_error_response):
        """Error raised during actual nodes read"""

        api = API(access_token=some_config["access_token"], page_size=100)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=["account_id", "account_currency"],
            insights_lookback_window=28,
        )
        requests_mock.register_uri("GET", f"{act_url}", [config_error_response, ad_account_response])
        try:
            slice = list(stream.stream_slices(sync_mode=SyncMode.full_refresh, stream_state={}))[0]
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice, stream_state={}))
            assert False
        except Exception as error:
            assert isinstance(error, AirbyteTracedException)
            assert error.failure_type == FailureType.config_error
            assert friendly_msg in error.message

    @pytest.mark.parametrize("name, friendly_msg, config_error_response", [CONFIG_ERRORS[0]])
    def test_config_error_insights_during_actual_nodes_read(self, requests_mock, name, friendly_msg, config_error_response):
        """Error raised during actual nodes read"""

        api = API(access_token=some_config["access_token"], page_size=100)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=["account_id", "account_currency"],
            insights_lookback_window=28,
        )
        requests_mock.register_uri("GET", f"{act_url}", [ad_account_response])
        requests_mock.register_uri("GET", f"{act_url}insights", [config_error_response, ad_creative_response])

        try:
            slice = list(stream.stream_slices(sync_mode=SyncMode.full_refresh, stream_state={}))[0]
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice, stream_state={}))
            assert False
        except Exception as error:
            assert isinstance(error, AirbyteTracedException)
            assert error.failure_type == FailureType.config_error
            assert friendly_msg in error.message

    def test_retry_for_cannot_include_error(self, requests_mock):
        """Error raised randomly for insights stream. Oncall: https://github.com/airbytehq/oncall/issues/4868"""

        api = API(access_token=some_config["access_token"], page_size=100)
        stream = AdsInsights(
            api=api,
            account_ids=some_config["account_ids"],
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2011, 1, 1),
            fields=["account_id", "account_currency"],
            insights_lookback_window=28,
        )
        requests_mock.register_uri("GET", f"{act_url}", [ad_account_response])
        response = {
            "status_code": 400,
            "json": {
                "error": {
                    "message": "(#100) Cannot include video_avg_time_watched_actions, video_continuous_2_sec_watched_actions in summary param because they weren't there while creating the report run.",
                    "type": "OAuthException",
                    "code": 100,
                }
            },
        }
        call_insights = requests_mock.register_uri("GET", f"{act_url}insights", [response])

        try:
            slice = list(stream.stream_slices(sync_mode=SyncMode.full_refresh, stream_state={}))[0]
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice, stream_state={}))
        except Exception:
            assert call_insights.call_count == 5

    @pytest.mark.parametrize(
        "failure_response",
        (
            {
                "status_code": 403,
                "json": {
                    "message": "(#200) Requires business_management permission to manage the object",
                    "type": "OAuthException",
                    "code": 200,
                    "fbtrace_id": "AOm48i-YaiRlzqnNEnECcW8",
                },
            },
            {
                "status_code": 400,
                "json": {
                    "message": "Unsupported request - method type: get",
                    "type": "GraphMethodException",
                    "code": 100,
                    "fbtrace_id": "AOm48i-YaiRlzqnNEnECcW8",
                },
            },
        ),
    )
    def test_adaccount_list_objects_retry(self, requests_mock, failure_response):
        """
        Sometimes we get an error: "Requires business_management permission to manage the object" when account has all the required permissions:
            [
                'ads_management',
                'ads_read',
                'business_management',
                'public_profile'
            ]
        As a workaround for this case we can retry the API call excluding `owner` from `?fields=` GET query param.
        """
        api = API(access_token=some_config["access_token"], page_size=100)
        stream = AdAccount(
            api=api,
            account_ids=some_config["account_ids"],
        )

        business_user = {
            "account_id": account_id,
            "business": {"id": "1", "name": "TEST"},
        }
        requests_mock.register_uri("GET", f"{base_url}me/business_users", status_code=200, json=business_user)

        assigend_users = {"account_id": account_id, "tasks": ["TASK"]}
        requests_mock.register_uri("GET", f"{act_url}assigned_users", status_code=200, json=assigend_users)

        success_response = {"status_code": 200, "json": {"account_id": account_id}}
        requests_mock.register_uri("GET", f"{act_url}", [failure_response, success_response])

        record_gen = stream.read_records(
            sync_mode=SyncMode.full_refresh,
            stream_slice={"account_id": account_id},
            stream_state={},
        )
        assert list(record_gen) == [{"account_id": "unknown_account", "id": "act_unknown_account"}]


def test_traced_exception_with_api_error():
    error = FacebookRequestError(
        message="Some error occurred",
        request_context={},
        http_status=400,
        http_headers={},
        body='{"error": {"message": "Error validating access token", "code": 190}}',
    )
    error.api_error_message = MagicMock(return_value="Error validating access token")

    result = traced_exception(error)

    assert isinstance(result, AirbyteTracedException)
    assert (
        result.message == "Invalid access token. Re-authenticate if FB oauth is used or refresh access token with all required permissions"
    )
    assert result.failure_type == FailureType.config_error


def test_traced_exception_without_api_error():
    error = FacebookRequestError(
        message="Call was unsuccessful. The Facebook API has imploded", request_context={}, http_status=408, http_headers={}, body="{}"
    )
    error.api_error_message = MagicMock(return_value=None)

    result = traced_exception(error)

    assert isinstance(result, AirbyteTracedException)
    assert result.message == "Error code 408: Call was unsuccessful. The Facebook API has imploded."
    assert result.failure_type == FailureType.system_error
