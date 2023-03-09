#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from contextlib import nullcontext as does_not_raise
from pathlib import Path

import pytest

from ci_connector_ops import utils

class TestConnector:

    @pytest.mark.parametrize(
        "technical_name, expected_type, expected_name, expected_error", 
        [
            ("source-faker", "source", "faker", does_not_raise()),
            ("source-facebook-marketing", "source", "facebook-marketing", does_not_raise()),
            ("destination-postgres", "destination", "postgres", does_not_raise()),
            ("foo", None, None, pytest.raises(utils.ConnectorInvalidNameError)),
        ])
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
        ])
    def test_init(self, connector, exists, mocker, tmp_path):
        assert str(connector) == connector.technical_name
        assert connector.connector_type, connector.name == connector._get_type_and_name_from_technical_name()
        assert connector.code_directory == Path(f"./airbyte-integrations/connectors/{connector.technical_name}")
        assert connector.acceptance_test_config_path == connector.code_directory / utils.ACCEPTANCE_TEST_CONFIG_FILE_NAME
        assert connector.documentation_file_path == Path(f"./docs/integrations/{connector.connector_type}s/{connector.name}.md")
        
        if exists:
            assert isinstance(connector.definition, dict)
            assert isinstance(connector.release_stage, str)
            assert isinstance(connector.acceptance_test_config, dict)
            assert connector.icon_path == Path(f"./airbyte-config/init/src/main/resources/icons/{connector.definition['icon']}")
            assert len(connector.version.split(".")) == 3
        else:
            assert connector.definition is None
            assert connector.release_stage is None
            assert connector.acceptance_test_config is None
            assert connector.icon_path == Path(f"./airbyte-config/init/src/main/resources/icons/{connector.name}.svg")
            with pytest.raises(FileNotFoundError):
                connector.version
            with pytest.raises(utils.ConnectorVersionNotFound):
                Path(tmp_path / "Dockerfile").touch()
                mocker.patch.object(utils.Connector, "code_directory", tmp_path)
                utils.Connector(connector.technical_name).version
