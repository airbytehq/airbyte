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
    end_date = "2021-05-04"
    conversion_window = 14
    response = chunk_date_range(start_date, end_date, conversion_window)
    assert [{'date': '2021-02-18'}, {'date': '2021-03-18'},
            {'date': '2021-04-18'}] == response
