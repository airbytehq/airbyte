#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_amazon_ads.utils import get_typed_env


def test_get_typed_env(monkeypatch):
    assert get_typed_env("REPORT_WAIT_TIMEOUT", 180) == 180
    assert get_typed_env("BOOLEAN_PARAM", "1") == "1"
    assert get_typed_env("STRING_PARAM", "string") == "string"
    monkeypatch.setenv("REPORT_WAIT_TIMEOUT", "60")
    assert get_typed_env("REPORT_WAIT_TIMEOUT", 180) == 60
    monkeypatch.setenv("REPORT_WAIT_TIMEOUT", "60")
    assert get_typed_env("REPORT_WAIT_TIMEOUT", "180") == "60"
    monkeypatch.setenv("REPORT_WAIT_TIMEOUT", "string")
    assert get_typed_env("REPORT_WAIT_TIMEOUT", 180) == 180
