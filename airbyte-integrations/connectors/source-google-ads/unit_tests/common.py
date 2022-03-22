#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from google.ads.googleads.errors import GoogleAdsException


class MockSearchRequest:
    customer_id = "12345"
    query = None
    page_size = 100
    page_token = None


# Mocking Classes
class MockGoogleAdsService:
    def search(self, search_request):
        return search_request


class MockGoogleAdsClient:
    def __init__(self, config):
        self.config = config

    def get_type(self, type):
        return MockSearchRequest()

    def get_service(self, service):
        return MockGoogleAdsService()

    @staticmethod
    def load_from_dict(config):
        return MockGoogleAdsClient(config)


class MockErroringGoogleAdsService:
    def search(self, search_request):
        raise GoogleAdsException("This mocked class always returns an error")


class MockErroringGoogleAdsClient:
    def __init__(self, config):
        self.config = config

    def get_type(self, type):
        return MockSearchRequest()

    def get_service(self, service):
        return MockErroringGoogleAdsService()

    @staticmethod
    def load_from_dict(config):
        return MockErroringGoogleAdsClient(config)
