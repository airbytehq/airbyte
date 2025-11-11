# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Base class for connector test suites."""

from __future__ import annotations

import inspect
import shutil
import sys
import tempfile
import warnings
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal, cast

import orjson
import pytest
import yaml
from boltons.typeutils import classproperty

from airbyte_cdk.models import (
    AirbyteCatalog,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.models.connector_metadata import MetadataFile
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.models import ConnectorTestScenario
from airbyte_cdk.utils.connector_paths import (
    ACCEPTANCE_TEST_CONFIG,
    find_connector_root,
)
from airbyte_cdk.utils.docker import (
    build_connector_image,
    run_docker_airbyte_command,
)


class DockerConnectorTestSuite:
    """Base class for connector test suites."""

    @classmethod
    def get_test_class_dir(cls) -> Path:
        """Get the file path that contains the class."""
        module = sys.modules[cls.__module__]
        # Get the directory containing the test file
        return Path(inspect.getfile(module)).parent

    @classmethod
    def get_connector_root_dir(cls) -> Path:
        """Get the root directory of the connector."""
        return find_connector_root([cls.get_test_class_dir(), Path.cwd()])

    @classproperty
    def connector_name(self) -> str:
        """Get the name of the connector."""
        connector_root = self.get_connector_root_dir()
        return connector_root.absolute().name

    @classmethod
    def is_destination_connector(cls) -> bool:
        """Check if the connector is a destination."""
        return cast(str, cls.connector_name).startswith("destination-")

    @classproperty
    def acceptance_test_config(cls) -> Any:
        """Get the contents of acceptance test config file.

        Also perform some basic validation that the file has the expected structure.
        """
        acceptance_test_config_path = cls.get_connector_root_dir() / ACCEPTANCE_TEST_CONFIG
        if not acceptance_test_config_path.exists():
            raise FileNotFoundError(
                f"Acceptance test config file not found at: {str(acceptance_test_config_path)}"
            )

        tests_config = yaml.safe_load(acceptance_test_config_path.read_text())

        if "acceptance_tests" not in tests_config:
            raise ValueError(
                f"Acceptance tests config not found in {acceptance_test_config_path}."
                f" Found only: {str(tests_config)}."
            )
        return tests_config

    @staticmethod
    def _dedup_scenarios(scenarios: list[ConnectorTestScenario]) -> list[ConnectorTestScenario]:
        """
        For FAST tests, we treat each config as a separate test scenario to run against, whereas CATs defined
        a series of more granular scenarios specifying a config_path and empty_streams among other things.

        This method deduplicates the CATs scenarios based on their config_path. In doing so, we choose to
        take the union of any defined empty_streams, to have high confidence that runnning a read with the
        config will not error on the lack of data in the empty streams or lack of permissions to read them.

        """
        deduped_scenarios: list[ConnectorTestScenario] = []

        for scenario in scenarios:
            for existing_scenario in deduped_scenarios:
                if scenario.config_path == existing_scenario.config_path:
                    # If a scenario with the same config_path already exists, we merge the empty streams.
                    # scenarios are immutable, so we create a new one.
                    all_empty_streams = (existing_scenario.empty_streams or []) + (
                        scenario.empty_streams or []
                    )
                    merged_scenario = existing_scenario.model_copy(
                        update={"empty_streams": list(set(all_empty_streams))}
                    )
                    deduped_scenarios.remove(existing_scenario)
                    deduped_scenarios.append(merged_scenario)
                    break
            else:
                # If a scenario does not exist with the config, add the new scenario to the list.
                deduped_scenarios.append(scenario)
        return deduped_scenarios

    @classmethod
    def get_scenarios(
        cls,
    ) -> list[ConnectorTestScenario]:
        """Get acceptance tests for a given category.

        This has to be a separate function because pytest does not allow
        parametrization of fixtures with arguments from the test class itself.
        """
        try:
            all_tests_config = cls.acceptance_test_config
        except FileNotFoundError as e:
            # Destinations sometimes do not have an acceptance tests file.
            warnings.warn(
                f"Acceptance test config file not found: {e!s}. No scenarios will be loaded.",
                category=UserWarning,
                stacklevel=1,
            )
            return []

        test_scenarios: list[ConnectorTestScenario] = []
        # we look in the basic_read section to find any empty streams
        for category in ["spec", "connection", "basic_read"]:
            if (
                category not in all_tests_config["acceptance_tests"]
                or "tests" not in all_tests_config["acceptance_tests"][category]
            ):
                continue

            for test in all_tests_config["acceptance_tests"][category]["tests"]:
                if "config_path" not in test:
                    # Skip tests without a config_path
                    continue

                if "iam_role" in test["config_path"]:
                    # We skip iam_role tests for now, as they are not supported in the test suite.
                    continue

                scenario = ConnectorTestScenario.model_validate(test)

                test_scenarios.append(scenario)

        deduped_test_scenarios = cls._dedup_scenarios(test_scenarios)

        return deduped_test_scenarios

    @pytest.mark.skipif(
        shutil.which("docker") is None,
        reason="docker CLI not found in PATH, skipping docker image tests",
    )
    @pytest.mark.image_tests
    def test_docker_image_build_and_spec(
        self,
        connector_image_override: str | None,
    ) -> None:
        """Run `docker_image` acceptance tests."""
        connector_root = self.get_connector_root_dir().absolute()
        metadata = MetadataFile.from_file(connector_root / "metadata.yaml")

        connector_image: str | None = connector_image_override
        if not connector_image:
            tag = "dev-latest"
            connector_image = build_connector_image(
                connector_name=connector_root.absolute().name,
                connector_directory=connector_root,
                metadata=metadata,
                tag=tag,
                no_verify=False,
            )

        _ = run_docker_airbyte_command(
            [
                "docker",
                "run",
                "--rm",
                connector_image,
                "spec",
            ],
            raise_if_errors=True,
        )

    @pytest.mark.skipif(
        shutil.which("docker") is None,
        reason="docker CLI not found in PATH, skipping docker image tests",
    )
    @pytest.mark.image_tests
    def test_docker_image_build_and_check(
        self,
        scenario: ConnectorTestScenario,
        connector_image_override: str | None,
    ) -> None:
        """Run `docker_image` acceptance tests.

        This test builds the connector image and runs the `check` command inside the container.

        Note:
          - It is expected for docker image caches to be reused between test runs.
          - In the rare case that image caches need to be cleared, please clear
            the local docker image cache using `docker image prune -a` command.
        """
        if scenario.expected_outcome.expect_exception():
            pytest.skip("Skipping test_docker_image_build_and_check (expected to fail).")

        tag = "dev-latest"
        connector_root = self.get_connector_root_dir()
        metadata = MetadataFile.from_file(connector_root / "metadata.yaml")
        connector_image: str | None = connector_image_override
        if not connector_image:
            tag = "dev-latest"
            connector_image = build_connector_image(
                connector_name=connector_root.absolute().name,
                connector_directory=connector_root,
                metadata=metadata,
                tag=tag,
                no_verify=False,
            )

        container_config_path = "/secrets/config.json"
        with scenario.with_temp_config_file(
            connector_root=connector_root,
        ) as temp_config_file:
            _ = run_docker_airbyte_command(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{temp_config_file}:{container_config_path}",
                    connector_image,
                    "check",
                    "--config",
                    container_config_path,
                ],
                raise_if_errors=True,
            )

    @pytest.mark.skipif(
        shutil.which("docker") is None,
        reason="docker CLI not found in PATH, skipping docker image tests",
    )
    @pytest.mark.image_tests
    def test_docker_image_build_and_read(
        self,
        scenario: ConnectorTestScenario,
        connector_image_override: str | None,
        read_from_streams: Literal["all", "none", "default"] | list[str],
        read_scenarios: Literal["all", "none", "default"] | list[str],
    ) -> None:
        """Read from the connector's Docker image.

        This test builds the connector image and runs the `read` command inside the container.

        Note:
          - It is expected for docker image caches to be reused between test runs.
          - In the rare case that image caches need to be cleared, please clear
            the local docker image cache using `docker image prune -a` command.
          - If the --connector-image arg is provided, it will be used instead of building the image.
        """
        if self.is_destination_connector():
            pytest.skip("Skipping read test for destination connector.")

        if scenario.expected_outcome.expect_exception():
            pytest.skip("Skipping (expected to fail).")

        if read_from_streams == "none":
            pytest.skip("Skipping read test (`--read-from-streams=false`).")

        if read_scenarios == "none":
            pytest.skip("Skipping (`--read-scenarios=none`).")

        default_scenario_ids = ["config", "valid_config", "default"]
        if read_scenarios == "all":
            pass
        elif read_scenarios == "default":
            if scenario.id not in default_scenario_ids:
                pytest.skip(
                    f"Skipping read test for scenario '{scenario.id}' "
                    f"(not in default scenarios list '{default_scenario_ids}')."
                )
        elif scenario.id not in read_scenarios:
            # pytest.skip(
            raise ValueError(
                f"Skipping read test for scenario '{scenario.id}' "
                f"(not in --read-scenarios={read_scenarios})."
            )

        tag = "dev-latest"
        connector_root = self.get_connector_root_dir()
        connector_name = connector_root.absolute().name
        metadata = MetadataFile.from_file(connector_root / "metadata.yaml")
        connector_image: str | None = connector_image_override
        if not connector_image:
            tag = "dev-latest"
            connector_image = build_connector_image(
                connector_name=connector_name,
                connector_directory=connector_root,
                metadata=metadata,
                tag=tag,
                no_verify=False,
            )

        container_config_path = "/secrets/config.json"
        container_catalog_path = "/secrets/catalog.json"

        with (
            scenario.with_temp_config_file(
                connector_root=connector_root,
            ) as temp_config_file,
            tempfile.TemporaryDirectory(
                prefix=f"{connector_name}-test",
                ignore_cleanup_errors=True,
            ) as temp_dir_str,
        ):
            temp_dir = Path(temp_dir_str)
            discover_result = run_docker_airbyte_command(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{temp_config_file}:{container_config_path}",
                    connector_image,
                    "discover",
                    "--config",
                    container_config_path,
                ],
                raise_if_errors=True,
            )

            catalog_message = discover_result.catalog  # Get catalog message
            assert catalog_message.catalog is not None, "Catalog message missing catalog."
            discovered_catalog: AirbyteCatalog = catalog_message.catalog
            if not discovered_catalog.streams:
                raise ValueError(
                    f"Discovered catalog for connector '{connector_name}' is empty. "
                    "Please check the connector's discover implementation."
                )

            streams_list = [stream.name for stream in discovered_catalog.streams]
            if read_from_streams == "default" and metadata.data.suggestedStreams:
                # set `streams_list` to be the intersection of discovered and suggested streams.
                streams_list = list(set(streams_list) & set(metadata.data.suggestedStreams.streams))

            if isinstance(read_from_streams, list):
                # If `read_from_streams` is a list, we filter the discovered streams.
                streams_list = list(set(streams_list) & set(read_from_streams))

            if scenario.empty_streams:
                # Filter out streams marked as empty in the scenario.
                empty_stream_names = [stream.name for stream in scenario.empty_streams]
                streams_list = [s for s in streams_list if s.name not in empty_stream_names]

            configured_catalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog(
                streams=[
                    ConfiguredAirbyteStream(
                        stream=stream,
                        sync_mode=(
                            stream.supported_sync_modes[0]
                            if stream.supported_sync_modes
                            else SyncMode.full_refresh
                        ),
                        destination_sync_mode=DestinationSyncMode.append,
                    )
                    for stream in discovered_catalog.streams
                    if stream.name in streams_list
                ]
            )
            configured_catalog_path = temp_dir / "catalog.json"
            configured_catalog_path.write_text(
                orjson.dumps(asdict(configured_catalog)).decode("utf-8")
            )
            read_result: EntrypointOutput = run_docker_airbyte_command(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-v",
                    f"{temp_config_file}:{container_config_path}",
                    "-v",
                    f"{configured_catalog_path}:{container_catalog_path}",
                    connector_image,
                    "read",
                    "--config",
                    container_config_path,
                    "--catalog",
                    container_catalog_path,
                ],
                raise_if_errors=True,
            )
