# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from connectors_qa.checks import assets
from connectors_qa.models import CheckStatus


class TestCheckConnectorIconIsAvailable:
    def test_fail_when_icon_path_does_not_exist(self, tmp_path, mocker):
        # Arrange
        connector = mocker.MagicMock()
        connector.icon_path = tmp_path / "icon.svg"

        # Act
        result = assets.CheckConnectorIconIsAvailable()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "Icon file is missing. Please create an icon file at the root of the connector code directory."

    def test_fail_when_icon_path_is_none(self, mocker):
        # Arrange
        connector = mocker.MagicMock()
        connector.icon_path = None

        # Act
        result = assets.CheckConnectorIconIsAvailable()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "Icon file is missing. Please create an icon file at the root of the connector code directory."

    def test_fail_when_icon_path_is_not_named_icon_svg(self, tmp_path, mocker):
        # Arrange
        connector = mocker.MagicMock()
        connector.icon_path = tmp_path / "icon.png"
        connector.icon_path.touch()

        # Act
        result = assets.CheckConnectorIconIsAvailable()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "Icon file is not named 'icon.svg'"

    def test_pass_when_icon_path_exists_and_is_named_icon_svg(self, tmp_path, mocker):
        # Arrange
        connector = mocker.MagicMock()
        connector.icon_path = tmp_path / "icon.svg"
        connector.icon_path.touch()

        # Act
        result = assets.CheckConnectorIconIsAvailable()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "Icon file exists"
