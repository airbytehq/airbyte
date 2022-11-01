#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_google_ads.models import Customer


def test_time_zone():
    mock_account_info = [[{"customer.id": "8765"}]]
    customers = Customer.from_accounts(mock_account_info)
    for customer in customers:
        assert customer.time_zone == "local"


@pytest.mark.parametrize("is_manager_account", (True, False))
def test_manager_account(is_manager_account):
    mock_account_info = [[{"customer.manager": is_manager_account, "customer.id": "8765"}]]
    customers = Customer.from_accounts(mock_account_info)
    for customer in customers:
        assert customer.is_manager_account is is_manager_account
