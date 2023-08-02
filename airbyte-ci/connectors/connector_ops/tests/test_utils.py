#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest
from connector_ops import utils


class TestConnector:
    @pytest.mark.parametrize(
        "technical_name, expected_type, expected_name, expected_error",
        [
            ("source-faker", "source", "faker", does_not_raise()),
            ("source-facebook-marketing", "source", "facebook-marketing", does_not_raise()),
            ("destination-postgres", "destination", "postgres", does_not_raise()),
            ("foo", None, None, pytest.raises(utils.ConnectorInvalidNameError)),
        ],
    )
    def test__get_type_and_name_from_technical_name(self, technical_name, expected_type, expected_name, expected_error):
        connector = utils.Connector(technical_name)
        with expected_error:
            assert connector._get_type_and_name_from_technical_name() == (expected_type, expected_name)
            assert connector.name == expected_name
            assert connector.connector_type == expected_type

    @pytest.mark.parametrize(
        "connector, exists",
        [
            (utils.Connector("source-faker"), True),
            (utils.Connector("source-notpublished"), False),
        ],
    )
    def test_init(self, connector, exists, mocker, tmp_path):
        assert str(connector) == connector.technical_name
        assert connector.connector_type, connector.name == connector._get_type_and_name_from_technical_name()
        assert connector.code_directory == Path(f"./airbyte-integrations/connectors/{connector.technical_name}")
        assert connector.acceptance_test_config_path == connector.code_directory / utils.ACCEPTANCE_TEST_CONFIG_FILE_NAME
        assert connector.documentation_file_path == Path(f"./docs/integrations/{connector.connector_type}s/{connector.name}.md")

        if exists:
            assert isinstance(connector.metadata, dict)
            assert isinstance(connector.release_stage, str)
            assert isinstance(connector.acceptance_test_config, dict)
            assert connector.icon_path == Path(f"./airbyte-config-oss/init-oss/src/main/resources/icons/{connector.metadata['icon']}")
            assert len(connector.version.split(".")) == 3
        else:
            assert connector.metadata is None
            assert connector.release_stage is None
            assert connector.acceptance_test_config is None
            assert connector.icon_path == Path(f"./airbyte-config-oss/init-oss/src/main/resources/icons/{connector.name}.svg")
            with pytest.raises(FileNotFoundError):
                connector.version
            with pytest.raises(utils.ConnectorVersionNotFound):
                Path(tmp_path / "Dockerfile").touch()
                mocker.patch.object(utils.Connector, "code_directory", tmp_path)
                utils.Connector(connector.technical_name).version


@pytest.fixture()
def gradle_file_with_dependencies(tmpdir) -> Path:
    test_gradle_file = Path(tmpdir) / "build.gradle"
    test_gradle_file.write_text(
        """
    plugins {
            id 'java'
    }

    dependencies {
        implementation project(':path:to:dependency1')
        implementation project(':path:to:dependency2')
        testImplementation project(':path:to:test:dependency')
        integrationTestJavaImplementation project(':path:to:test:dependency1')
        performanceTestJavaImplementation project(':path:to:test:dependency2')
    }
    """
    )
    expected_dependencies = [Path("path/to/dependency1"), Path("path/to/dependency2")]
    expected_test_dependencies = [Path("path/to/test/dependency"), Path("path/to/test/dependency1"), Path("path/to/test/dependency2")]

    return test_gradle_file, expected_dependencies, expected_test_dependencies


def test_parse_dependencies(gradle_file_with_dependencies):
    gradle_file, expected_regular_dependencies, expected_test_dependencies = gradle_file_with_dependencies
    regular_dependencies, test_dependencies = utils.parse_dependencies(gradle_file)
    assert len(regular_dependencies) == len(expected_regular_dependencies)
    assert all([regular_dependency in expected_regular_dependencies for regular_dependency in regular_dependencies])
    assert len(test_dependencies) == len(expected_test_dependencies)
    assert all([test_dependency in expected_test_dependencies for test_dependency in test_dependencies])


@pytest.mark.parametrize("with_test_dependencies", [True, False])
def test_get_all_gradle_dependencies(with_test_dependencies):
    build_file = Path("airbyte-integrations/connectors/source-postgres-strict-encrypt/build.gradle")
    if with_test_dependencies:
        all_dependencies = utils.get_all_gradle_dependencies(build_file)
        expected_dependencies = [
            Path("airbyte-db/db-lib"),
            Path("airbyte-json-validation"),
            Path("airbyte-config-oss/config-models-oss"),
            Path("airbyte-commons"),
            Path("airbyte-test-utils"),
            Path("airbyte-api"),
            Path("airbyte-connector-test-harnesses/acceptance-test-harness"),
            Path("airbyte-commons-protocol"),
            Path("airbyte-integrations/bases/base-java"),
            Path("airbyte-commons-cli"),
            Path("airbyte-integrations/bases/base"),
            Path("airbyte-integrations/connectors/source-postgres"),
            Path("airbyte-integrations/bases/debezium"),
            Path("airbyte-integrations/connectors/source-jdbc"),
            Path("airbyte-integrations/connectors/source-relational-db"),
            Path("airbyte-integrations/bases/standard-source-test"),
        ]
        assert len(all_dependencies) == len(expected_dependencies)
        assert all([dependency in expected_dependencies for dependency in all_dependencies])
    else:
        all_dependencies = utils.get_all_gradle_dependencies(build_file, with_test_dependencies=False)
        expected_dependencies = [
            Path("airbyte-db/db-lib"),
            Path("airbyte-json-validation"),
            Path("airbyte-config-oss/config-models-oss"),
            Path("airbyte-commons"),
            Path("airbyte-integrations/bases/base-java"),
            Path("airbyte-commons-cli"),
            Path("airbyte-integrations/bases/base"),
            Path("airbyte-integrations/connectors/source-postgres"),
            Path("airbyte-integrations/bases/debezium"),
            Path("airbyte-integrations/connectors/source-jdbc"),
            Path("airbyte-integrations/connectors/source-relational-db"),
        ]
        assert len(all_dependencies) == len(expected_dependencies)
        assert all([dependency in expected_dependencies for dependency in all_dependencies])
