# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from source_paypal_transaction import SourcePaypalTransaction


def test_source():
    assert SourcePaypalTransaction()