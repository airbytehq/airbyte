# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from connectors_qa.checks import documentation
from connectors_qa.models import CheckStatus


class TestCheckMigrationGuide:
    def test_passed_when_no_breaking_changes(self, mocker):
        # Arrange
        connector = mocker.Mock(technical_name="test-connector", metadata={}, migration_guide_file_path=None)

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert "No breaking changes found. A migration guide is not required" in result.message

    def test_fail_when_migration_guide_file_path_does_not_exists(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(
            technical_name="test-connector",
            metadata={"releases": {"breakingChanges": {"1.0.0": "Description"}}},
            migration_guide_file_path=tmp_path / "not_existing_migration_guide.md",
        )

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Migration guide file is missing " in result.message
        assert connector.technical_name in result.message
        assert "Please create a migration guide in" in result.message

    def test_fail_when_migration_guide_file_path_is_none(self, mocker):
        # Arrange
        connector = mocker.Mock(
            technical_name="test-connector",
            metadata={"releases": {"breakingChanges": {"1.0.0": "Description"}}},
            migration_guide_file_path=None,
        )

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Migration guide file is missing " in result.message
        assert connector.technical_name in result.message
        assert "Please create a migration guide in" in result.message

    def test_fail_when_migration_guide_file_does_not_start_with_correct_header(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(
            name_from_metadata="Test Connector",
            technical_name="test-connector",
            metadata={"releases": {"breakingChanges": {"1.0.0": "Description"}}},
            migration_guide_file_path=tmp_path / "migration_guide.md",
        )
        connector.migration_guide_file_path.write_text("")

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Migration guide file for test-connector does not start with the correct header" in result.message
        assert "Expected '# Test Connector Migration Guide', got ''" in result.message

    def test_fail_when_migration_guide_file_has_missing_version_headings(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(
            name_from_metadata="Test Connector",
            technical_name="test-connector",
            metadata={"releases": {"breakingChanges": {"1.0.0": "Description", "2.0.0": "Description"}}},
            migration_guide_file_path=tmp_path / "migration_guide.md",
        )
        connector.migration_guide_file_path.write_text("# Test Connector Migration Guide\n## Upgrading to 1.0.0\n")

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"Migration guide file for {connector.name_from_metadata} has incorrect version headings" in result.message
        assert "Expected headings: ['## Upgrading to 2.0.0', '## Upgrading to 1.0.0']" in result.message

    def test_fail_when_migration_guide_file_has_invalid_version_headings(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(
            name_from_metadata="Test Connector",
            technical_name="test-connector",
            metadata={"releases": {"breakingChanges": {"1.0.0": "Description", "2.0.0": "Description"}}},
            migration_guide_file_path=tmp_path / "migration_guide.md",
        )
        connector.migration_guide_file_path.write_text("# Test Connector Migration Guide\n## Upgrade to 1.0.0\n")

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"Migration guide file for {connector.name_from_metadata} has incorrect version headings" in result.message
        assert "Expected headings: ['## Upgrading to 2.0.0', '## Upgrading to 1.0.0']" in result.message

    def test_fail_when_migration_guide_file_has_ascending_version_headings(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(
            name_from_metadata="Test Connector",
            technical_name="test-connector",
            metadata={"releases": {"breakingChanges": {"1.0.0": "Description", "2.0.0": "Description"}}},
            migration_guide_file_path=tmp_path / "migration_guide.md",
        )
        connector.migration_guide_file_path.write_text("# Test Connector Migration Guide\n## Upgrading to 1.0.0\n## Upgrading to 2.0.0\n")

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"Migration guide file for {connector.name_from_metadata} has incorrect version headings" in result.message
        assert "Expected headings: ['## Upgrading to 2.0.0', '## Upgrading to 1.0.0']" in result.message

    def test_fail_when_migration_guide_file_has_incorrect_version_headings(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(
            name_from_metadata="Test Connector",
            technical_name="test-connector",
            metadata={"releases": {"breakingChanges": {"1.0.0": "Description", "2.0.0": "Description"}}},
            migration_guide_file_path=tmp_path / "migration_guide.md",
        )
        connector.migration_guide_file_path.write_text("# Test Connector Migration Guide\n## Upgrading to 1.0.0\n## Upgrading to 3.0.0\n")

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"Migration guide file for {connector.name_from_metadata} has incorrect version headings" in result.message
        assert "Expected headings: ['## Upgrading to 2.0.0', '## Upgrading to 1.0.0']" in result.message

    def test_pass_when_migration_guide_file_has_correct_version_headings(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(
            name_from_metadata="Test Connector",
            technical_name="test-connector",
            metadata={"releases": {"breakingChanges": {"1.0.0": "Description", "2.0.0": "Description"}}},
            migration_guide_file_path=tmp_path / "migration_guide.md",
        )
        connector.migration_guide_file_path.write_text("# Test Connector Migration Guide\n## Upgrading to 2.0.0\n## Upgrading to 1.0.0\n")

        # Act
        result = documentation.CheckMigrationGuide()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert "The migration guide is correctly templated" in result.message


class TestCheckDocumentationExists:
    def test_fail_when_documentation_file_path_is_none(self, mocker):
        # Arrange
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=None)

        # Act
        result = documentation.CheckDocumentationExists()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "User facing documentation file is missing. Please create it" in result.message

    def test_fail_when_documentation_file_path_does_not_exists(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=tmp_path / "not_existing_documentation.md")

        # Act
        result = documentation.CheckDocumentationExists()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "User facing documentation file is missing. Please create it" in result.message

    def test_pass_when_documentation_file_path_exists(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=documentation_file_path)
        connector.documentation_file_path.write_text("")

        # Act
        result = documentation.CheckDocumentationExists()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert f"User facing documentation file {documentation_file_path} exists" in result.message


class TestCheckDocumentationStructure:
    def test_fail_when_documentation_file_path_does_not_exists(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=tmp_path / "not_existing_documentation.md")

        # Act
        result = documentation.CheckDocumentationStructure()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Could not check documentation structure as the documentation file is missing" in result.message

    def test_fail_when_documentation_file_path_is_none(self, mocker):
        # Arrange
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=None)

        # Act
        result = documentation.CheckDocumentationStructure()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Could not check documentation structure as the documentation file is missing" in result.message

    def test_fail_when_documentation_file_is_empty(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=documentation_file_path)
        connector.documentation_file_path.write_text("")

        # Act
        result = documentation.CheckDocumentationStructure()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Documentation file is empty" in result.message

    def test_fail_when_documentation_file_does_not_start_with_correct_header(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(
            technical_name="test-connector", metadata={"name": "Test Connector"}, documentation_file_path=documentation_file_path
        )
        connector.documentation_file_path.write_text("# Test Another connector")

        # Act
        result = documentation.CheckDocumentationStructure()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Connector documentation does not follow the guidelines:" in result.message
        assert "The connector name is not used as the main header in the documentation. Expected: '# Test Connector'" in result.message

    def test_fail_when_documentation_file_has_missing_sections(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(
            technical_name="test-connector", metadata={"name": "Test Connector"}, documentation_file_path=documentation_file_path
        )
        connector.documentation_file_path.write_text("# Test Connector")

        # Act
        result = documentation.CheckDocumentationStructure()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Connector documentation does not follow the guidelines:" in result.message
        for section in documentation.CheckDocumentationStructure.expected_sections:
            assert f"Connector documentation is missing a '{section.replace('#', '').strip()}' section" in result.message

    def test_pass_when_documentation_file_has_correct_structure(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(
            technical_name="test-connector", metadata={"name": "Test Connector"}, documentation_file_path=documentation_file_path
        )
        connector.documentation_file_path.write_text(
            "# Test Connector\n## Prerequisites\n## Setup guide\n## Supported sync modes\n## Supported streams\n## Changelog"
        )

        # Act
        result = documentation.CheckDocumentationStructure()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert "Documentation guidelines are followed" in result.message


class TestCheckChangelogEntry:
    def test_fail_when_documentation_file_path_does_not_exists(self, mocker, tmp_path):
        # Arrange
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=tmp_path / "not_existing_documentation.md")

        # Act
        result = documentation.CheckChangelogEntry()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Could not check changelog entry as the documentation file is missing. Please create it." in result.message

    def test_fail_when_documentation_file_path_is_none(self, mocker):
        # Arrange
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=None)

        # Act
        result = documentation.CheckChangelogEntry()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Could not check changelog entry as the documentation file is missing. Please create it." in result.message

    def test_fail_when_documentation_file_is_empty(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=documentation_file_path)
        connector.documentation_file_path.write_text("")

        # Act
        result = documentation.CheckChangelogEntry()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Documentation file is empty" in result.message

    def test_fail_when_documentation_file_doesnt_have_changelog_section(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(technical_name="test-connector", documentation_file_path=documentation_file_path)
        connector.documentation_file_path.write_text("# Test Connector")

        # Act
        result = documentation.CheckChangelogEntry()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Connector documentation is missing a 'Changelog' section" in result.message

    def test_fail_when_documentation_file_doesnt_have_changelog_entry(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(technical_name="test-connector", version="1.0.0", documentation_file_path=documentation_file_path)
        connector.documentation_file_path.write_text("# Test Connector\n## Changelog")

        # Act
        result = documentation.CheckChangelogEntry()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Connectors must have a changelog entry for each version: changelog entry for version 1.0.0" in result.message

    def test_pass_when_documentation_file_has_changelog_entry(self, mocker, tmp_path):
        # Arrange
        documentation_file_path = tmp_path / "documentation.md"
        connector = mocker.Mock(technical_name="test-connector", version="1.0.0", documentation_file_path=documentation_file_path)
        connector.documentation_file_path.write_text("# Test Connector\n## Changelog\n- Version 1.0.0")

        # Act
        result = documentation.CheckChangelogEntry()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert f"Changelog entry found for version 1.0.0" in result.message
