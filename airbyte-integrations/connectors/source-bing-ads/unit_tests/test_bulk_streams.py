#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from unittest.mock import patch

import source_bing_ads
from source_bing_ads.base_streams import Accounts
from source_bing_ads.bulk_streams import AppInstallAds


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

