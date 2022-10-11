#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from copy import deepcopy

from pytest import fixture


@fixture(name="config")
def config_fixture(requests_mock):
    return {
        "site_urls": ["https://example.com/"],
        "start_date": "2022-01-01",
        "end_date": "2022-02-01",
        "authorization": {
            "auth_type": "Client",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
        },
        "custom_reports": '[{"name": "custom_dimensions", "dimensions": ["date", "country", "device"]}]',
    }


@fixture
def config_gen(config):
    def inner(**kwargs):
        new_config = deepcopy(config)
        # WARNING, no support deep dictionaries
        new_config.update(kwargs)
        return {k: v for k, v in new_config.items() if v is not ...}

    return inner
