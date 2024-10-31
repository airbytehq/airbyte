#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.declarative.transformations.keys_to_lower_transformation import KeysToLowerTransformation

_ANY_VALUE = -1


def test_transform() -> None:
    record = {"wIth_CapITal": _ANY_VALUE, "anOThEr_witH_Caps": _ANY_VALUE}
    KeysToLowerTransformation().transform(record)
    assert {"with_capital": _ANY_VALUE, "another_with_caps": _ANY_VALUE}
