#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from source_s3.v4 import Config, SourceS3
from source_s3.v4.check_section import (
    CHECK_SECTION_KEY,
    declared_sections,
    requested_section,
    section_spec,
    strip_check_section,
)

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


def test_declared_sections_are_in_form_order():
    assert declared_sections() == ["bucket", "files", "review"]
    assert [section["id"] for section in Config.schema()["sections"]] == declared_sections()


def test_requested_section_is_none_without_the_key():
    assert requested_section({"bucket": "b"}) is None


@pytest.mark.parametrize("section", ["bucket", "files", "review"])
def test_requested_section_resolves_a_declared_section(section):
    assert requested_section({CHECK_SECTION_KEY: section, "bucket": "b"}) == section


def test_requested_section_rejects_an_unknown_section():
    with pytest.raises(AirbyteTracedException) as exc_info:
        requested_section({CHECK_SECTION_KEY: "credentials"})
    assert exc_info.value.failure_type == FailureType.config_error
    assert exc_info.value.message == "Unknown check-section 'credentials'; the connector specification declares: bucket, files, review."


@pytest.mark.parametrize("value", [1, "", " ", ["bucket"], {"id": "bucket"}])
def test_requested_section_rejects_a_non_string_section(value):
    with pytest.raises(AirbyteTracedException) as exc_info:
        requested_section({CHECK_SECTION_KEY: value})
    assert exc_info.value.failure_type == FailureType.config_error
    assert exc_info.value.message == "'check-section' must be a non-empty string."


def test_strip_check_section_removes_the_key_only():
    assert strip_check_section({CHECK_SECTION_KEY: "bucket", "bucket": "b", "endpoint": ""}) == {"bucket": "b", "endpoint": ""}


def test_section_spec_for_the_bucket_section_requires_the_bucket_fields_only():
    spec = SourceS3.create().spec()

    narrowed = section_spec(spec, "bucket")

    assert narrowed.connectionSpecification["required"] == ["credentials", "bucket"]
    assert narrowed.connectionSpecification["properties"] == spec.connectionSpecification["properties"]
    assert narrowed.documentationUrl == spec.documentationUrl
    # The full spec is left untouched.
    assert spec.connectionSpecification["required"] == ["streams", "credentials", "bucket"]


def test_section_spec_for_the_files_section_requires_the_streams_too():
    spec = SourceS3.create().spec()

    narrowed = section_spec(spec, "files")

    assert narrowed.connectionSpecification["required"] == ["streams", "credentials", "bucket"]


def test_section_spec_for_the_last_section_is_the_full_spec():
    spec = SourceS3.create().spec()

    assert section_spec(spec, "review") is spec
