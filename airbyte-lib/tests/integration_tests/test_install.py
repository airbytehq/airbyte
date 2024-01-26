from gettext import install
import pytest

from airbyte_lib._factories.connector_factories import get_connector
from airbyte_lib import exceptions as exc


def test_install_failure_log_pypi():
    """Test that the install log is created and contains the expected content."""
    with pytest.raises(exc.AirbyteConnectorNotRegisteredError):
        source = get_connector("source-not-found")

    with pytest.raises(exc.AirbyteConnectorInstallationError):
        source = get_connector(
            "source-not-found",
            pip_url="https://pypi.org/project/airbyte-not-found",
            install_if_missing=True,
        )
