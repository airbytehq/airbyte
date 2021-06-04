from source_google_ads.source import chunk_date_range, SourceGoogleAds
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteCatalog, Type
from datetime import date
from dateutil.relativedelta import *

{
    "developer_token": "developer_token",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "refresh_token": "refresh_token",
    "start_date": "start_date",
    "customer_id": "customer_id"
}


SAMPLE_CATALOG = {
    "streams": [
        {
            "stream": {
                "name": "ad_group_ad_report",
                "json_schema": {
                    "type": "object",
                    "title": "Ad Group Ad Report",
                    "description": "An ad group ad.",
                    "properties": {
                        "accent_color": {
                            "description": "AccentColor",
                            "type": ["null", "string"],
                            "field": "ad_group_ad.ad.legacy_responsive_display_ad.accent_color"
                        },
                        "account_currency_code": {
                            "description": "AccountCurrencyCode",
                            "type": ["null", "string"],
                            "field": "customer.currency_code"
                        },
                        "account_descriptive_name": {
                            "description": "AccountDescriptiveName",
                            "type": ["null", "string"],
                            "field": "customer.descriptive_name"
                        },
                        "date": {
                            "description": "Date",
                            "type": ["null", "string"],
                            "field": "segments.date"
                        }
                    }
                },
                "supported_sync_modes": ["full_refresh", "incremental"],
                "source_defined_cursor": True,
                "default_cursor_field": ["date"]
            },
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
            "cursor_field": ["date"]
        }
    ]
}


def test_chunk_date_range():
    start_date = "2021-03-04"
    conversion_window = 14
    response = chunk_date_range(start_date, conversion_window)
    assert [{'date': '2021-02-18'}, {'date': '2021-03-18'},
            {'date': '2021-04-18'}, {'date': '2021-05-18'}] == response


"""
This won't work until we get sample credentials 
"""

# def test_incremental_sync():
#     google_ads_client = SourceGoogleAds()
#     state = "2021-05-24"
#     records = google_ads_client.read(AirbyteLogger(), SAMPLE_CONFIG, ConfiguredAirbyteCatalog.parse_obj(SAMPLE_CATALOG), {"ad_group_ad_report": {
#         "date": state
#     }})
#     current_state = (date.fromisoformat(state) -
#                      relativedelta(days=14)).isoformat()
#     for record in records:
#         if record and record.type == Type.STATE:
#             current_state = record.state.data["ad_group_ad_report"]["date"]
#         if record and record.type == Type.RECORD:
#             assert record.record.data["date"] >= current_state

#     # Next sync
#     state = "2021-06-04"
#     records = google_ads_client.read(AirbyteLogger(), SAMPLE_CONFIG, ConfiguredAirbyteCatalog.parse_obj(SAMPLE_CATALOG), {"ad_group_ad_report": {
#         "date": state
#     }})
#     current_state = (date.fromisoformat(state) -
#                      relativedelta(days=14)).isoformat()

#     for record in records:
#         if record and record.type == Type.STATE:
#             current_state = record.state.data["ad_group_ad_report"]["date"]
#         if record and record.type == Type.RECORD:
#             assert record.record.data["date"] >= current_state

#     # Abnormal state
#     state = "2029-06-04"
#     records = google_ads_client.read(AirbyteLogger(), SAMPLE_CONFIG, ConfiguredAirbyteCatalog.parse_obj(SAMPLE_CATALOG), {"ad_group_ad_report": {
#         "date": state
#     }})
#     current_state = (date.fromisoformat(state) -
#                      relativedelta(days=14)).isoformat()

#     no_records = True
#     for record in records:
#         if record and record.type == Type.STATE:
#             assert record.state.data["ad_group_ad_report"]["date"] == state
#         if record and record.type == Type.RECORD:
#             no_records = False

#     assert no_records == True
