# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from connector_ops.utils import ConnectorLanguage
from connectors_qa import consts
from connectors_qa.checks import ENABLED_CHECKS
from connectors_qa.models import CheckStatus


class TestCheck:
    def test_fail_when_requires_metadata_and_metata_is_missing(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={})

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
        connector = mocker.MagicMock(language=None)

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
