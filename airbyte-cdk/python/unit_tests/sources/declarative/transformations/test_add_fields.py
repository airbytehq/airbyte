#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

import pytest
from airbyte_cdk.sources.declarative.transformations import AddFields
from airbyte_cdk.sources.declarative.transformations.add_fields import AddedFieldDefinition
from airbyte_cdk.sources.declarative.types import FieldPointer


@pytest.mark.parametrize(
    ["input_record", "field", "kwargs", "expected"],
    [()],
)
def test_remove_fields(
    input_record: Mapping[str, Any], field: List[Tuple[FieldPointer, str]], kwargs: Mapping[str, Any], expected: Mapping[str, Any]
):
    inputs = [AddedFieldDefinition(v[0], v[1]) for v in field]
    assert AddFields(inputs).transform(input_record) == expected
