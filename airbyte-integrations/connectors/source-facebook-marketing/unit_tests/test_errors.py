import json
from datetime import datetime

import pytest
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from facebook_business import FacebookAdsApi, FacebookSession
from source_facebook_marketing.api import API
from source_facebook_marketing.streams import AdCreatives, AdsInsights

FB_API_VERSION = FacebookAdsApi.API_VERSION

account_id = 'unknown_account'
some_config = {
    "start_date": "2021-01-23T00:00:00Z",
    "account_id": account_id,
    "access_token": "unknown_token"
}
act_url = f"{FacebookSession.GRAPH}/{FB_API_VERSION}/act_{account_id}/"

ad_account_response = {
    "json": {
        "data": [{"account_id": account_id, "id": f"act_{account_id}"}],
        "status_code": 200,
    }
}
ad_creative_data = [
    {"id": "111111", "name": "ad creative 1", "updated_time": "2023-03-21T22:33:56-0700"},
    {"id": "222222", "name": "ad creative 2", "updated_time": "2023-03-22T22:33:56-0700"},
]
ad_creative_response = {
    "json": {
        "data": ad_creative_data,
        "status_code": 200,
    }
}

#     "name, friendly_msg, config_error_response",
CONFIG_ERRORS = [
    ("error_400_validating_access_token_session_expired",
     "Re-authenticate or update access token",
     {
         "status_code": 400,
         "json": {
             "error": {
                 "message": "Error validating access token: Session has expired on Friday, 18-Aug",
                 "type": "OAuthException",
                 "code": 190,
                 "error_subcode": 463,
             }
         }
     }
     ),
    ("error_400_validating_access_token_user_changed_their_password",
     "Re-authenticate or update access token",
     {
         "status_code": 400,
         "json": {
             "error": {
                 "message": "Error validating access token: The session has been invalidated because the user changed their password or Facebook has changed the session for security reasons",
                 "type": "OAuthException",
                 "code": 190,
                 "error_subcode": 460,
             }
         }
     }
     ),
    ("error_400_validating_access_token_not_authorized_application",
     "Re-authenticate or update access token",
     {
         "status_code": 400,
         "json": {
             "error": {
                 "message": "Error validating access token: The user has not authorized application 2586347315015828.",
                 "type": "OAuthException",
                 "code": 190,
                 "error_subcode": 458,
                 "fbtrace_id": "A3pz5DCfhBg3mGCS6Z9z9zY"
             }
         }
     }
     ),
    ("error_400_missing_permission",
     "Re-authenticate to check whether correct Ad Account ID",
     {
         "status_code": 400,
         "json": {
             "error": {
                 "message": "(#100) Missing permissions",
                 "type": "OAuthException",
                 "code": 100,
             }
         }
     }
     ),
    ("error_403_requires_permission",
     "Re-authenticate because current credential missing permissions",
     {
         "status_code": 403,
         "json": {
             "error": {
                 "code": 200,
                 "message": "(#200) Requires business_management permission to manage the object",
             }
         }
     }
     ),

    ("error_400_permission_must_be_granted",
     "Re-authenticate because current credential missing permissions",
     {
         "status_code": 400,
         "json": {
             "error": {
                 "message": "Any of the pages_read_engagement, pages_manage_metadata,\n        pages_read_user_content, pages_manage_ads, pages_show_list or\n        pages_messaging permission(s) must be granted before impersonating a\n        user's page.",
                 "type": "OAuthException",
                 "code": 190,
             }
         }
     }
     ),
    ("error_unsupported_get_request",
     "Re-authenticate because current credential missing permissions",
     {
         "json": {
             "error": {
                 "message": "Unsupported get request. Object with ID 'xxx' does not exist, cannot be loaded due to missing permissions, or does not support this operation. Please read the Graph API documentation at https://developers.facebook.com/docs/graph-api",
                 "type": "GraphMethodException",
                 "code": 100,
                 "error_subcode": 33,
                 "fbtrace_id": "A7qVRrTcBm8Pt6iUvnBrxwf"
             }
         },
         "status_code": 400,  # ???????????????????
     }
     ),
    ("error_400_unknown",
     "Re-authenticate because current credential missing permissions",
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
         }
     })
]


class TestRealErrors:
    @pytest.mark.parametrize(
        "name, retryable_error_response",
        [
            ("error_400_too_many_calls",
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
             }
             ),
            ("error_500_unknown",
             {
                 "json": {
                     "error": {
                         "code": 1,
                         "message": "An unknown error occurred",
                         "error_subcode": 99
                     }
                 },
                 "status_code": 500,
             }
             ),
            ("error_400_service_temporarily_unavailable",
             {
                 "status_code": 400,
                 "json": {
                     "error": {
                         "message": "(#2) Service temporarily unavailable",
                         "type": "OAuthException",
                         "is_transient": True,
                         "code": 2,
                         "fbtrace_id": "AnUyGZoFqN2m50GHVpOQEqr"
                     }
                 }
             }
             )
        ]
    )
    def test_retryable_error(self, some_config, requests_mock, name, retryable_error_response):
        """Error once, check that we retry and not fail"""
        requests_mock.reset_mock()
        requests_mock.register_uri("GET", f"{act_url}", [retryable_error_response, ad_account_response])
        requests_mock.register_uri("GET", f"{act_url}adcreatives", [retryable_error_response, ad_creative_response])

        api = API(account_id=some_config["account_id"], access_token=some_config["access_token"], page_size=100)
        stream = AdCreatives(api=api, include_deleted=False)
        ad_creative_records = list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))

        assert ad_creative_records == ad_creative_data

        # requests_mock.register_uri("GET", f"{self.act_url}advideos", [error_400_service_temporarily_unavailable, ad_creative_response])
        # stream = Videos(api=api, start_date=pendulum.now(), end_date=pendulum.now(), include_deleted=False, page_size=100)

    @pytest.mark.parametrize("name, friendly_msg, config_error_response", CONFIG_ERRORS)
    def test_config_error_during_account_info_read(self, requests_mock, name, friendly_msg, config_error_response):
        """Error raised during account info read"""

        api = API(account_id=some_config["account_id"], access_token=some_config["access_token"], page_size=100)
        stream = AdCreatives(api=api, include_deleted=False)

        requests_mock.register_uri("GET", f"{act_url}", [config_error_response, ad_account_response])
        try:
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))
            assert False
        except Exception as error:
            assert isinstance(error, AirbyteTracedException)
            assert error.failure_type == FailureType.config_error
            assert friendly_msg in error.message

    @pytest.mark.parametrize("name, friendly_msg, config_error_response", [CONFIG_ERRORS[-1]])
    def test_config_error_during_actual_nodes_read(self, requests_mock, name, friendly_msg, config_error_response):
        """Error raised during actual nodes read"""

        api = API(account_id=some_config["account_id"], access_token=some_config["access_token"], page_size=100)
        stream = AdCreatives(api=api, include_deleted=False)

        requests_mock.register_uri("GET", f"{act_url}", [ad_account_response])
        requests_mock.register_uri("GET", f"{act_url}adcreatives", [config_error_response, ad_creative_response])
        try:
            list(stream.read_records(sync_mode=SyncMode.full_refresh, stream_state={}))
            assert False
        except Exception as error:
            assert isinstance(error, AirbyteTracedException)
            assert error.failure_type == FailureType.config_error
            assert friendly_msg in error.message

    @pytest.mark.parametrize("name, friendly_msg, config_error_response", CONFIG_ERRORS)
    def test_config_error_insights_account_info_read(self, requests_mock, name, friendly_msg, config_error_response):
        """Error raised during actual nodes read"""

        api = API(account_id=some_config["account_id"], access_token=some_config["access_token"], page_size=100)
        stream = AdsInsights(
            api=api,
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
    def test_config_error_insights_during_actual_nodes_read(self, requests_mock, name, friendly_msg,
                                                            config_error_response):
        """Error raised during actual nodes read"""

        api = API(account_id=some_config["account_id"], access_token=some_config["access_token"], page_size=100)
        stream = AdsInsights(
            api=api,
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
