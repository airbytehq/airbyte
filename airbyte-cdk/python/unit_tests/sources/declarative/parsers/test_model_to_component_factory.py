#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.declarative.checks import CheckStream
from airbyte_cdk.sources.declarative.models import CheckStream as CheckStreamModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory


def test_create_check_stream():
    manifest = {"check": {"type": "CheckStream", "stream_names": ["list_stream"]}}

    factory = ModelToComponentFactory()

    check = factory.create_component(CheckStreamModel, manifest["check"], {})

    assert isinstance(check, CheckStream)
    assert check.stream_names == ["list_stream"]


def test_create_component_type_mismatch():
    manifest = {"check": {"type": "MismatchType", "stream_names": ["list_stream"]}}

    factory = ModelToComponentFactory()

    with pytest.raises(ValueError):
        factory.create_component(CheckStreamModel, manifest["check"], {})
