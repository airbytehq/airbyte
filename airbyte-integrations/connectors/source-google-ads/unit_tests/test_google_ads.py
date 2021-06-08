from source_google_ads.google_ads import GoogleAds
from string import Template
from datetime import date


SAMPLE_SCHEMA = {
    "json_schema": {
        "properties": {
            "segment.date": {
                "type": ["null", "string"],
            }
        }
    }
}


# Mocking Classes
class MockGoogleAdsService:
    def search(self, search_request):
        return search_request


class MockedDateSegment:
    def __init__(self, date: str):
        self._mock_date = date

    def __getattr__(self, attr):
        if attr == 'date':
            return date.fromisoformat(self._mock_date)
        return MockedDateSegment(self._mock_date)


class MockSearchRequest:
    customer_id = "12345"
    query = None
    page_size = 100
    page_token = None


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


SAMPLE_CONFIG = {
    "developer_token": "developer_token",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "refresh_token": "refresh_token",
    "customer_id": "customer_id"
}

EXPECTED_CRED = {"developer_token": "developer_token",
                 "client_id": "client_id",
                 "client_secret": "client_secret",
                 "refresh_token": "refresh_token", }


def test_google_ads_init(mocker):
    google_client_mocker = mocker.patch("source_google_ads.google_ads.GoogleAdsClient",
                                        return_value=MockGoogleAdsClient)
    google_ads_client = GoogleAds(**SAMPLE_CONFIG)
    assert google_ads_client.customer_id == SAMPLE_CONFIG["customer_id"]
    assert google_client_mocker.load_from_dict.call_args[0][0] == EXPECTED_CRED


def test_send_request(mocker):
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.load_from_dict",
                 return_value=MockGoogleAdsClient(SAMPLE_CONFIG))
    mocker.patch("source_google_ads.google_ads.GoogleAdsClient.get_service",
                 return_value=MockGoogleAdsService())
    google_ads_client = GoogleAds(**SAMPLE_CONFIG)
    query = "Query"
    page_size = 1000
    response = google_ads_client.send_request(query)

    assert response.customer_id == SAMPLE_CONFIG["customer_id"]
    assert response.query == query
    assert response.page_size == page_size


def test_get_fields_from_schema():
    response = GoogleAds.get_fields_from_schema(SAMPLE_SCHEMA)
    assert response == ["segment.date"]


def test_convert_schema_into_query():
    report_name = "ad_group_ad_report"
    query = Template("""
          SELECT
            segment.date
          FROM ad_group_ad
          WHERE segments.date > '2020-01-01'
            AND segments.date < '2020-03-01'
          ORDER BY segments.date
      """)
    response = GoogleAds.convert_schema_into_query(
        SAMPLE_SCHEMA, report_name, "2020-01-01", "2020-03-01")
    assert response == query.substitute()


def test_get_field_value():
    field = "segment.date"
    date = "2001-01-01"
    response = GoogleAds.get_field_value(MockedDateSegment(date), field)
    assert response == date
    date = "2020"
    response = GoogleAds.get_field_value(MockedDateSegment(date), field)
    assert response == None


def test_parse_single_result():
    date = "2001-01-01"
    response = GoogleAds.parse_single_result(
        SAMPLE_SCHEMA, MockedDateSegment(date))
    assert response == response
