import os
from hashlib import md5
from pathlib import Path
from typing import Any, cast

import yaml
from boltons.typeutils import classproperty

from airbyte_cdk.sources.declarative.concurrent_declarative_source import (
    ConcurrentDeclarativeSource,
)
from airbyte_cdk.test.models import ConnectorTestScenario
from airbyte_cdk.test.standard_tests._job_runner import IConnector
from airbyte_cdk.test.standard_tests.source_base import SourceTestSuiteBase
from airbyte_cdk.utils.connector_paths import MANIFEST_YAML


def md5_checksum(file_path: Path) -> str:
    """Helper function to calculate the MD5 checksum of a file.

    This is used to calculate the checksum of the `components.py` file, if it exists.
    """
    with open(file_path, "rb") as file:
        return md5(file.read()).hexdigest()


class DeclarativeSourceTestSuite(SourceTestSuiteBase):
    """Declarative source test suite.

    This inherits from the Python-based source test suite and implements the
    `create_connector` method to create a declarative source object instead of
    requiring a custom Python source object.

    The class also automatically locates the `manifest.yaml` file and the
    `components.py` file (if it exists) in the connector's directory.
    """

    connector: type[IConnector] | None = None

    @classproperty
    def manifest_yaml_path(cls) -> Path:
        """Get the path to the manifest.yaml file."""
        result = cls.get_connector_root_dir() / MANIFEST_YAML
        if result.exists():
            return result

        raise FileNotFoundError(
            f"Manifest YAML file not found at {result}. "
            "Please ensure that the test suite is run in the correct directory.",
        )

    @classproperty
    def components_py_path(cls) -> Path | None:
        """Get the path to the `components.py` file, if one exists.

        If not `components.py` file exists, return None.
        """
        result = cls.get_connector_root_dir() / "components.py"
        if result.exists():
            return result

        return None

    @classmethod
    def create_connector(
        cls,
        scenario: ConnectorTestScenario | None,
    ) -> IConnector:
        """Create a connector scenario for the test suite.

        This overrides `create_connector` from the create a declarative source object
        instead of requiring a custom python source object.

        Subclasses should not need to override this method.
        """
        scenario = scenario or ConnectorTestScenario()  # Use default (empty) scenario if None
        manifest_dict = yaml.safe_load(cls.manifest_yaml_path.read_text())
        config = {
            "__injected_manifest": manifest_dict,
        }
        config.update(
            scenario.get_config_dict(
                empty_if_missing=True,
                connector_root=cls.get_connector_root_dir(),
            ),
        )

        if cls.components_py_path and cls.components_py_path.exists():
            os.environ["AIRBYTE_ENABLE_UNSAFE_CODE"] = "true"
            config["__injected_components_py"] = cls.components_py_path.read_text()
            config["__injected_components_py_checksums"] = {
                "md5": md5_checksum(cls.components_py_path),
            }

        return cast(
            IConnector,
            ConcurrentDeclarativeSource(
                config=config,
                catalog=None,
                state=None,
                source_config=manifest_dict,
            ),
        )
