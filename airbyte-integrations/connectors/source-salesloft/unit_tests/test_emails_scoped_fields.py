# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from conftest import TEST_CONFIG, get_source
from freezegun import freeze_time

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


SALESLOFT_API_URL = "https://api.salesloft.com/v2"
SCOPED_FIELDS_ERROR = "Requested scoped field(s) could not be returned, required scope access not included."


def read_from_stream(stream_name: str, sync_mode: SyncMode, expecting_exception: bool = False):
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(get_source(TEST_CONFIG), TEST_CONFIG, catalog, expecting_exception=expecting_exception)


@freeze_time("2026-05-23T07:30:16Z")
def test_emails_scoped_fields_missing_scope_access_is_config_error(requests_mock):
    requests_mock.get(
        f"{SALESLOFT_API_URL}/activities/emails",
        json={"error": SCOPED_FIELDS_ERROR},
        status_code=422,
    )

    output = read_from_stream("emails_scoped_fields", SyncMode.incremental, expecting_exception=True)

    assert not output.records
    assert output.errors
    assert output.errors[0].trace.error.failure_type == FailureType.config_error
    assert "Salesloft email content access is required for the emails_scoped_fields stream." in output.get_formatted_error_message()
    assert "Disable this stream or grant the token access to email_contents:read scoped fields." in output.get_formatted_error_message()
