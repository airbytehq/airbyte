#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import Mock

import pytest
from pendulum.tz.timezone import Timezone
from source_google_ads.models import CustomerModel


def test_time_zone(mocker):
    mocker.patch("source_google_ads.models.local_timezone", Mock(return_value=Timezone("Europe/Riga")))

    mock_account_info = [{"customer_client.id": "8765"}]
    customers = CustomerModel.from_accounts(mock_account_info)
    for customer in customers:
        assert customer.time_zone.name == Timezone("Europe/Riga").name


@pytest.mark.parametrize("is_manager_account", (True, False))
def test_manager_account(is_manager_account):
    mock_account_info = [{"customer_client.manager": is_manager_account, "customer_client.id": "8765"}]
    customers = CustomerModel.from_accounts(mock_account_info)
    for customer in customers:
        assert customer.is_manager_account is is_manager_account
