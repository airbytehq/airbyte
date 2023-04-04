#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.utils.utils import peek


@pytest.mark.parametrize(
   "test_name, iterable, expected_first",
   [
       ("test_empty_iterable", [], None),
       ("test_empty_two_values", [1, 2], 1),
   ]
)
def test_peek(test_name, iterable, expected_first):
    iterator = iter(iterable)
    first, returned_iterator = peek(iterator)
    assert first == expected_first
    assert [_ for _ in returned_iterator] == iterable
