# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from connector_ops.utils import ConnectorLanguage
from connectors_qa import consts
from connectors_qa.checks import ENABLED_CHECKS
from connectors_qa.models import CheckStatus


class TestCheck:
    def test_fail_when_requires_metadata_and_metata_is_missing(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={}, is_released=False)

        # Act
        results = []
        for check in ENABLED_CHECKS:
            if check.requires_metadata:
                results.append(check.run(connector))

        # Assert
        assert all(result.status == CheckStatus.FAILED for result in results)
        assert all(
            result.message
            == f"This checks requires metadata file to run. Please add {consts.METADATA_FILE_NAME} file to the connector code directory."
            for result in results
        )

    def test_fail_when_language_is_missing(self, mocker):
        # Arrange
        connector = mocker.MagicMock(language=None, is_released=False)

        # Act
        results = []
        for check in ENABLED_CHECKS:
            results.append(check.run(connector))

        # Assert
        assert all(result.status == CheckStatus.FAILED for result in results)
        assert all(result.message == "Connector language could not be inferred" for result in results)

    def test_skip_when_language_does_not_apply(self, mocker):
        # Arrange
        connector = mocker.MagicMock(language=ConnectorLanguage.JAVA)

        # Act
        results = []
        for check in ENABLED_CHECKS:
            if connector.language not in check.applies_to_connector_languages:
                results.append(check.run(connector))

        # Assert
        assert all(result.status == CheckStatus.SKIPPED for result in results)

    def test_skip_when_type_does_not_apply(self, mocker):
        # Arrange
        connector = mocker.MagicMock(connector_type="destination")

        # Act
        results = []
        for check in ENABLED_CHECKS:
            if connector.connector_type not in check.applies_to_connector_types:
                results.append(check.run(connector))

        # Assert
        assert all(result.status == CheckStatus.SKIPPED for result in results)

    def test_skip_when_check_does_not_apply_to_released_connectors(self, mocker):
        # Arrange
        connector = mocker.MagicMock(is_released=True)

        # Act
        results = []
        for check in ENABLED_CHECKS:
            if not check.runs_on_released_connectors:
                results.append(check.run(connector))

        # Assert
        assert all(result.status == CheckStatus.SKIPPED for result in results)
        assert all(result.message == "Check does not apply to released connectors" for result in results)

    def test_skip_when_connector_support_level_does_not_apply_to(self, mocker):
        # Arrange
        connector = mocker.MagicMock(support_level="community")

        # Act
        results = []
        for check in ENABLED_CHECKS:
            if check.applies_to_connector_support_levels and connector.support_level not in check.applies_to_connector_support_levels:
                results.append(check.run(connector))

        # Assert
        assert all(result.status == CheckStatus.SKIPPED for result in results)
