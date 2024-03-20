#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from unittest.mock import patch

import pendulum
import pytest
import source_bing_ads
from freezegun import freeze_time
from pendulum import UTC, DateTime
from source_bing_ads.base_streams import Accounts
from source_bing_ads.bulk_streams import AppInstallAdLabels, AppInstallAds


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_stream_slices(mocked_client, config):
    slices = AppInstallAds(mocked_client, config).stream_slices()
    assert list(slices) == []

    app_install_ads = AppInstallAds(mocked_client, config)
    accounts_read_records = iter([{"Id": 180519267, "ParentCustomerId": 100}, {"Id": 180278106, "ParentCustomerId": 200}])
    with patch.object(Accounts, "read_records", return_value=accounts_read_records):
        slices = app_install_ads.stream_slices()
        assert list(slices) == [{"account_id": 180519267, "customer_id": 100}, {"account_id": 180278106, "customer_id": 200}]


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_transform(mocked_client, config):
    record = {"Ad Group": "Ad Group", "App Id": "App Id", "Campaign": "Campaign", "Custom Parameter": "Custom Parameter"}
    transformed_record = AppInstallAds(mocked_client, config).transform(
        record=record, stream_slice={"account_id": 180519267, "customer_id": 100}
    )
    assert transformed_record == {
        "Account Id": 180519267,
        "Ad Group": "Ad Group",
        "App Id": "App Id",
        "Campaign": "Campaign",
        "Custom Parameter": "Custom Parameter",
    }


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_read_with_chunks(mocked_client, config):
    path_to_file = Path(__file__).parent / "app_install_ads.csv"
    path_to_file_base = Path(__file__).parent / "app_install_ads_base.csv"
    with open(path_to_file_base, "r") as f1, open(path_to_file, "a") as f2:
        for line in f1:
            f2.write(line)

    app_install_ads = AppInstallAds(mocked_client, config)
    result = app_install_ads.read_with_chunks(path=path_to_file)
    assert next(result) == {
        "Ad Group": "AdGroupNameGoesHere",
        "App Id": "AppStoreIdGoesHere",
        "App Platform": "Android",
        "Campaign": "ParentCampaignNameGoesHere",
        "Client Id": "ClientIdGoesHere",
        "Custom Parameter": "{_promoCode}=PROMO1; {_season}=summer",
        "Destination Url": None,
        "Device Preference": "All",
        "Display Url": None,
        "Final Url": "FinalUrlGoesHere",
        "Final Url Suffix": None,
        "Id": None,
        "Mobile Final Url": None,
        "Modified Time": None,
        "Name": None,
        "Parent Id": "-1111",
        "Promotion": None,
        "Status": "Active",
        "Text": "Find New Customers & Increase Sales!",
        "Title": "Contoso Quick Setup",
        "Tracking Template": None,
        "Type": "App Install Ad",
    }


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_read_with_chunks_app_install_ad_labels(mocked_client, config):
    path_to_file = Path(__file__).parent / "app_install_ad_labels.csv"
    path_to_file_base = Path(__file__).parent / "app_install_ad_labels_base.csv"
    with open(path_to_file_base, "r") as f1, open(path_to_file, "a") as f2:
        for line in f1:
            f2.write(line)

    app_install_ads = AppInstallAdLabels(mocked_client, config)
    result = app_install_ads.read_with_chunks(path=path_to_file)
    assert next(result) == {
        'Ad Group': None,
        'Campaign': None,
        'Client Id': 'ClientIdGoesHere',
        'Color': None,
        'Description': None,
        'Id': '-22',
        'Label': None,
        'Modified Time': None,
        'Name': None,
        'Parent Id': '-11112',
        'Status': None,
        'Type': 'App Install Ad Label'
    }


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_read_with_chunks_ioe_error(mocked_client, config, caplog):
    app_install_ads = AppInstallAdLabels(mocked_client, config)
    with pytest.raises(IOError):
        list(app_install_ads.read_with_chunks(path=Path(__file__).parent / "non-existing-file.csv"))
    assert "The IO/Error occurred while reading tmp data" in caplog.text


@patch.object(source_bing_ads.source, "Client")
@freeze_time("2023-11-01T12:00:00.000+00:00")
@pytest.mark.parametrize(
    "stream_state, config_start_date, expected_start_date",
    [
        ({"some_account_id": {"Modified Time": "2023-10-15T12:00:00.000+00:00"}}, "2020-01-01", DateTime(2023, 10, 15, 12, 0, 0, tzinfo=UTC)),
        ({"another_account_id": {"Modified Time": "2023-10-15T12:00:00.000+00:00"}}, "2020-01-01", None),
        ({}, "2020-01-01", None),
        ({}, "2023-10-21", DateTime(2023, 10, 21, 0, 0, 0, tzinfo=UTC)),
    ],
    ids=["state_within_30_days", "state_within_30_days_another_account_id", "empty_state", "empty_state_start_date_within_30"]
)
def test_bulk_stream_start_date(mocked_client, config, stream_state, config_start_date, expected_start_date):
    mocked_client.reports_start_date = pendulum.parse(config_start_date) if config_start_date else None
    stream = AppInstallAds(mocked_client, config)
    assert expected_start_date == stream.get_start_date(stream_state, 'some_account_id')


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_stream_state(mocked_client, config):
    stream = AppInstallAds(mocked_client, config)
    stream.state = {"Account Id": "some_account_id", "Modified Time": "04/27/2023 18:00:14.970"}
    assert stream.state == {"some_account_id": {"Modified Time": "2023-04-27T18:00:14.970+00:00"}}
    stream.state = {"Account Id": "some_account_id", "Modified Time": "05/27/2023 18:00:14.970"}
    assert stream.state == {"some_account_id": {"Modified Time": "2023-05-27T18:00:14.970+00:00"}}
    stream.state = {"Account Id": "some_account_id", "Modified Time": "05/25/2023 18:00:14.970"}
    assert stream.state == {"some_account_id": {"Modified Time": "2023-05-27T18:00:14.970+00:00"}}
    # stream state saved to connection state
    stream.state = {
        "120342748234": {
            "Modified Time": "2022-11-05T12:07:29.360+00:00"
        },
        "27364572345": {
            "Modified Time": "2022-11-05T12:07:29.360+00:00"
        },
        "732645723": {
            "Modified Time": "2022-11-05T12:07:29.360+00:00"
        },
        "837563864": {
            "Modified Time": "2022-11-05T12:07:29.360+00:00"
        }
    }
    assert stream.state == {
        "120342748234": {"Modified Time": "2022-11-05T12:07:29.360+00:00"},
        "27364572345": {"Modified Time": "2022-11-05T12:07:29.360+00:00"},
        "732645723": {"Modified Time": "2022-11-05T12:07:29.360+00:00"},
        "837563864": {"Modified Time": "2022-11-05T12:07:29.360+00:00"},
        "some_account_id": {"Modified Time": "2023-05-27T18:00:14.970+00:00"},
    }


@patch.object(source_bing_ads.source, "Client")
def test_bulk_stream_custom_transform_date_rfc3339(mocked_client, config):
    stream = AppInstallAds(mocked_client, config)
    assert "2023-04-27T18:00:14.970+00:00" == stream.custom_transform_date_rfc3339("04/27/2023 18:00:14.970", stream.get_json_schema()["properties"][stream.cursor_field])
