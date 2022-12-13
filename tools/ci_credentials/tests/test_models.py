#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import pytest
from ci_credentials.models import Secret


@pytest.mark.parametrize(
    "connector_name,filename,expected_name, expected_directory",
    (
        ("source-default", "config.json", "SECRET_SOURCE-DEFAULT__CREDS", "airbyte-integrations/connectors/source-default/secrets"),
        (
            "source-custom-filename-1",
            "config_custom.json",
            "SECRET_SOURCE-CUSTOM-FILENAME-1_CUSTOM__CREDS",
            "airbyte-integrations/connectors/source-custom-filename-1/secrets",
        ),
        (
            "source-custom-filename-2",
            "auth.json",
            "SECRET_SOURCE-CUSTOM-FILENAME-2_AUTH__CREDS",
            "airbyte-integrations/connectors/source-custom-filename-2/secrets",
        ),
        (
            "source-custom-filename-3",
            "config_auth-test---___---config.json",
            "SECRET_SOURCE-CUSTOM-FILENAME-3_AUTH-TEST__CREDS",
            "airbyte-integrations/connectors/source-custom-filename-3/secrets",
        ),
        (
            "source-custom-filename-4",
            "_____config_test---config.json",
            "SECRET_SOURCE-CUSTOM-FILENAME-4_TEST__CREDS",
            "airbyte-integrations/connectors/source-custom-filename-4/secrets",
        ),
        (
            "base-normalization",
            "_____config_test---config.json",
            "SECRET_BASE-NORMALIZATION_TEST__CREDS",
            "airbyte-integrations/bases/base-normalization/secrets",
        ),
    ),
)
def test_secret_instantiation(connector_name, filename, expected_name, expected_directory):
    secret = Secret(connector_name, filename, "secret_value")
    assert secret.name == expected_name
    assert secret.directory == expected_directory
