#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


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
