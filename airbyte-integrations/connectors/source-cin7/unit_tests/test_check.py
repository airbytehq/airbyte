# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import logging

from conftest import get_source

from airbyte_cdk.models import Status
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {
    "accountid": "account-id",
    "api_key": "api-key",
}


def test_check_uses_sale_list_instead_of_bank_accounts():
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest("https://inventory.dearsystems.com/externalapi/v2/ref/accountBank?page=1&limit=1000"),
            HttpResponse(body="Incorrect credentials!", status_code=403),
        )
        http_mocker.get(
            HttpRequest("https://inventory.dearsystems.com/externalapi/v2/saleList?page=1&limit=1000"),
            HttpResponse(body='{"SaleList": []}', status_code=200),
        )

        result = get_source(config=CONFIG).check(logger=logging.getLogger("airbyte"), config=CONFIG)

    assert result.status == Status.SUCCEEDED
