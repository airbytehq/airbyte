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
            (utils.Connector("source-doesnotexist"), False),
        ],
    )
    def test_init(self, connector, exists, mocker, tmp_path):
        assert str(connector) == connector.technical_name
        assert connector.code_directory == Path(f"./airbyte-integrations/connectors/{connector.technical_name}")
        assert connector.acceptance_test_config_path == connector.code_directory / utils.ACCEPTANCE_TEST_CONFIG_FILE_NAME

        if exists:
            assert connector.connector_type, connector.name == connector._get_type_and_name_from_technical_name()
            assert connector.documentation_file_path == Path(f"./docs/integrations/{connector.connector_type}s/{connector.name}.md")
            assert isinstance(connector.metadata, dict)
            assert isinstance(connector.support_level, str)
            assert isinstance(connector.acceptance_test_config, dict)
            assert connector.icon_path == Path(f"./airbyte-integrations/connectors/{connector.technical_name}/icon.svg")
            assert len(connector.version.split(".")) == 3
        else:
            assert connector.metadata is None
            assert connector.support_level is None
            assert connector.acceptance_test_config is None
            assert connector.icon_path == Path(f"./airbyte-integrations/connectors/{connector.technical_name}/icon.svg")
            assert connector.version is None
            with pytest.raises(utils.ConnectorVersionNotFound):
                Path(tmp_path / "Dockerfile").touch()
                mocker.patch.object(utils.Connector, "code_directory", tmp_path)
                utils.Connector(connector.technical_name).version

    def test_metadata_query_match(self, mocker):
        connector = utils.Connector("source-faker")
        mocker.patch.object(utils.Connector, "metadata", {"dockerRepository": "airbyte/source-faker", "ab_internal": {"ql": 100}})
        assert connector.metadata_query_match("data.dockerRepository == 'airbyte/source-faker'")
        assert connector.metadata_query_match("'source' in data.dockerRepository")
        assert not connector.metadata_query_match("data.dockerRepository == 'airbyte/source-faker2'")
        assert not connector.metadata_query_match("'destination' in data.dockerRepository")
        assert connector.metadata_query_match("data.ab_internal.ql == 100")
        assert connector.metadata_query_match("data.ab_internal.ql >= 100")
        assert connector.metadata_query_match("data.ab_internal.ql > 1")
        assert not connector.metadata_query_match("data.ab_internal.ql == 101")
        assert not connector.metadata_query_match("data.ab_internal.ql >= 101")
        assert not connector.metadata_query_match("data.ab_internal.ql > 101")
        assert not connector.metadata_query_match("data.ab_internal == whatever")

    @pytest.fixture
    def connector_without_dockerfile(self, mocker, tmp_path):
        mocker.patch.object(utils.Connector, "code_directory", tmp_path)
        connector = utils.Connector("source-faker")
        return connector

    def test_has_dockerfile_without_dockerfile(self, connector_without_dockerfile):
        assert not connector_without_dockerfile.has_dockerfile

    @pytest.fixture
    def connector_with_dockerfile(self, mocker, tmp_path):
        mocker.patch.object(utils.Connector, "code_directory", tmp_path)
        connector = utils.Connector("source-faker")
        tmp_path.joinpath("Dockerfile").touch()
        return connector

    def test_has_dockerfile_with_dockerfile(self, connector_with_dockerfile):
        assert connector_with_dockerfile.has_dockerfile


@pytest.fixture()
def gradle_file_with_dependencies(tmpdir) -> tuple[Path, list[Path], list[Path]]:
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


@pytest.fixture()
def gradle_file_with_local_cdk_dependencies(tmpdir) -> tuple[Path, list[Path], list[Path]]:
    test_gradle_file = Path(tmpdir) / "build.gradle"
    test_gradle_file.write_text(
        """
    plugins {
        id 'java'
        id 'airbyte-java-connector'
    }

    airbyteJavaConnector {
        cdkVersionRequired = '0.1.0'
        features = ['db-destinations']
        useLocalCdk = true
    }

    airbyteJavaConnector.addCdkDependencies()

    dependencies {
        implementation project(':path:to:dependency1')
        implementation project(':path:to:dependency2')
        testImplementation project(':path:to:test:dependency')
        integrationTestJavaImplementation project(':path:to:test:dependency1')
        performanceTestJavaImplementation project(':path:to:test:dependency2')
    }
    """
    )
    expected_dependencies = [
        Path("path/to/dependency1"),
        Path("path/to/dependency2"),
    ]
    expected_test_dependencies = [
        Path("path/to/test/dependency"),
        Path("path/to/test/dependency1"),
        Path("path/to/test/dependency2"),
    ]
    return test_gradle_file, expected_dependencies, expected_test_dependencies


def test_parse_dependencies(gradle_file_with_dependencies):
    gradle_file, expected_regular_dependencies, expected_test_dependencies = gradle_file_with_dependencies
    regular_dependencies, test_dependencies = utils.parse_gradle_dependencies(gradle_file)
    assert len(regular_dependencies) == len(expected_regular_dependencies)
    assert all([regular_dependency in expected_regular_dependencies for regular_dependency in regular_dependencies])
    assert len(test_dependencies) == len(expected_test_dependencies)
    assert all([test_dependency in expected_test_dependencies for test_dependency in test_dependencies])


def test_parse_dependencies_with_cdk(gradle_file_with_local_cdk_dependencies):
    gradle_file, expected_regular_dependencies, expected_test_dependencies = gradle_file_with_local_cdk_dependencies
    regular_dependencies, test_dependencies = utils.parse_gradle_dependencies(gradle_file)
    assert len(regular_dependencies) == len(expected_regular_dependencies)
    assert all([regular_dependency in expected_regular_dependencies for regular_dependency in regular_dependencies])
    assert len(test_dependencies) == len(expected_test_dependencies)
    assert all([test_dependency in expected_test_dependencies for test_dependency in test_dependencies])


def test_get_all_connectors_in_repo():
    all_connectors = utils.get_all_connectors_in_repo()
    assert len(all_connectors) > 0
    for connector in all_connectors:
        assert isinstance(connector, utils.Connector)
        assert connector.metadata is not None
        if connector.has_airbyte_docs and connector.is_enabled_in_any_registry:
            assert connector.documentation_file_path.exists()
