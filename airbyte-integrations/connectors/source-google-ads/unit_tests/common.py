#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v11.errors.types.authorization_error import AuthorizationErrorEnum
from google.ads.googleads.v13 import GoogleAdsFailure
from google.ads.googleads.v13.errors.types.authentication_error import AuthenticationErrorEnum
from google.ads.googleads.v13.errors.types.query_error import QueryErrorEnum
from google.ads.googleads.v13.errors.types.quota_error import QuotaErrorEnum


class MockSearchRequest:
    customer_id = "12345"
    query = None
    page_size = 100
    page_token = None
    next_page_token = None


# Mocking Classes
class MockGoogleAdsService:
    def search(self, search_request):
        return search_request


class MockGoogleAdsClient:
    def __init__(self, credentials, **kwargs):
        self.config = credentials
        self.customer_ids = ["1"]

    def get_type(self, type):
        return MockSearchRequest()

    def get_service(self, service):
        if service == "GoogleAdsFieldService":
            return MockGoogleAdsFieldService()
        return MockGoogleAdsService()

    @staticmethod
    def load_from_dict(config, version=None):
        return MockGoogleAdsClient(config)

    def send_request(self, query, customer_id):
        yield from ()


class MockGoogleAdsFieldService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MockGoogleAdsFieldService, cls).__new__(cls)
            cls._instance.request_query = None
        return cls._instance

    def search_google_ads_fields(self, request):
        self.request_query = request.query

        class MockResponse:
            def __init__(self, name):
                self.name = name

        fields = [name.strip("'") for name in request.query.split("WHERE name in (")[1].split(")")[0].split(",")]
        return [MockResponse(name) for name in fields]


def make_google_ads_exception(failure_code: int = 1, failure_msg: str = "it failed", error_type: str = "requestError"):
    # There is no easy way I could find to mock a GoogleAdsException without doing something heinous like this
    # Following the definition of the object here
    # https://developers.google.com/google-ads/api/reference/rpc/v10/GoogleAdsFailure
    protobuf_as_json = json.dumps({"errors": [{"error_code": {error_type: failure_code}, "message": failure_msg}], "request_id": "1"})
    failure = GoogleAdsFailure.from_json(protobuf_as_json)
    return GoogleAdsException(None, None, failure, 1)


ERROR_MAP = {
    "CUSTOMER_NOT_FOUND": {"failure_code": AuthenticationErrorEnum.AuthenticationError.CUSTOMER_NOT_FOUND, "failure_msg": "msg2",
                           "error_type": "authenticationError"},
    "USER_PERMISSION_DENIED": {"failure_code": AuthorizationErrorEnum.AuthorizationError.USER_PERMISSION_DENIED, "failure_msg": "msg1",
                               "error_type": "authorizationError"},
    "CUSTOMER_NOT_ENABLED": {"failure_code": AuthorizationErrorEnum.AuthorizationError.CUSTOMER_NOT_ENABLED, "failure_msg": "msg2",
                             "error_type": "authorizationError"},
    "QUERY_ERROR": {"failure_code": QueryErrorEnum.QueryError.UNEXPECTED_END_OF_QUERY,
                    "failure_msg": "Error in query: unexpected end of query.", "error_type": "queryError"},
    "RESOURCE_EXHAUSTED": {"failure_code": QuotaErrorEnum.QuotaError.RESOURCE_EXHAUSTED, "failure_msg": "msg4", "error_type": "quotaError"},
    "UNEXPECTED_ERROR": {"failure_code": AuthorizationErrorEnum.AuthorizationError.UNKNOWN, "failure_msg": "Unexpected error message",
                         "error_type": "authorizationError"}
}


def mock_google_ads_request_failure(mocker, error_name):
    param = ERROR_MAP[error_name]
    # Extract the parameter values from the request object
    failure_code = param.get("failure_code", 1)
    failure_msg = param.get("failure_msg", "it failed")
    error_type = param.get("error_type", "request_error")

    exception = make_google_ads_exception(failure_code=failure_code, failure_msg=failure_msg, error_type=error_type)

    mocker.patch("source_google_ads.google_ads.GoogleAds.send_request", side_effect=exception)
