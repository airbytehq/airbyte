# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import textwrap
from typing import List

from connector_ops.utils import Connector  # type: ignore
from connectors_qa import consts
from connectors_qa.models import Check, CheckCategory, CheckResult
from pydash.objects import get  # type: ignore


class DocumentationCheck(Check):
    category = CheckCategory.DOCUMENTATION


class CheckMigrationGuide(DocumentationCheck):
    name = "Breaking changes must be accompanied by a migration guide"
    description = "When a breaking change is introduced, we check that a migration guide is available. It should be stored under `./docs/integrations/<connector-type>s/<connector-name>-migrations.md`.\nThis document should contain a section for each breaking change, in order of the version descending. It must explain users which action to take to migrate to the new version."

    def _run(self, connector: Connector) -> CheckResult:
        breaking_changes = get(connector.metadata, "releases.breakingChanges")
        if not breaking_changes:
            return self.create_check_result(
                connector=connector,
                passed=True,
                message="No breaking changes found. A migration guide is not required",
            )
        migration_guide_file_path = connector.migration_guide_file_path
        migration_guide_exists = migration_guide_file_path is not None and migration_guide_file_path.exists()
        if not migration_guide_exists:
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"Migration guide file is missing for {connector.technical_name}. Please create a migration guide in ./docs/integrations/<connector-type>s/<connector-name>-migrations.md`",
            )

        expected_title = f"# {connector.name_from_metadata} Migration Guide"
        expected_version_header_start = "## Upgrading to "
        migration_guide_content = migration_guide_file_path.read_text()
        try:
            first_line = migration_guide_content.splitlines()[0]
        except IndexError:
            first_line = migration_guide_content
        if not first_line == expected_title:
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"Migration guide file for {connector.technical_name} does not start with the correct header. Expected '{expected_title}', got '{first_line}'",
            )

        # Check that the migration guide contains a section for each breaking change key ## Upgrading to {version}
        # Note that breaking change is a dict where the version is the key
        # Note that the migration guide must have the sections in order of the version descending
        # 3.0.0, 2.0.0, 1.0.0, etc
        # This means we have to record the headings in the migration guide and then check that they are in order
        # We also have to check that the headings are in the breaking changes dict
        ordered_breaking_changes = sorted(breaking_changes.keys(), reverse=True)
        ordered_expected_headings = [f"{expected_version_header_start}{version}" for version in ordered_breaking_changes]

        ordered_heading_versions = []
        for line in migration_guide_content.splitlines():
            stripped_line = line.strip()
            if stripped_line.startswith(expected_version_header_start):
                version = stripped_line.replace(expected_version_header_start, "")
                ordered_heading_versions.append(version)

        if ordered_breaking_changes != ordered_heading_versions:
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=textwrap.dedent(
                    f"""
                Migration guide file for {connector.name_from_metadata} has incorrect version headings.
                Check for missing, extra, or misordered headings, or headers with typos.
                Expected headings: {ordered_expected_headings}
                """
                ),
            )
        return self.create_check_result(
            connector=connector,
            passed=True,
            message="The migration guide is correctly templated",
        )


class CheckDocumentationExists(DocumentationCheck):
    name = "Connectors must have user facing documentation"
    description = (
        "The user facing connector documentation should be stored under `./docs/integrations/<connector-type>s/<connector-name>.md`."
    )

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.documentation_file_path or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="User facing documentation file is missing. Please create it under ./docs/integrations/<connector-type>s/<connector-name>.md",
            )
        return self.pass_(
            connector=connector,
            message=f"User facing documentation file {connector.documentation_file_path} exists",
        )


class CheckDocumentationStructure(DocumentationCheck):
    name = "Connectors documentation follows our guidelines"
    description = f"The user facing connector documentation should follow the guidelines defined in the [documentation standards]({consts.DOCUMENTATION_STANDARDS_URL})."

    expected_sections = [
        "## Prerequisites",
        "## Setup guide",
        "## Supported sync modes",
        "## Supported streams",
        "## Changelog",
    ]

    def check_main_header(self, connector: Connector, doc_lines: List[str]) -> List[str]:
        errors = []
        if not doc_lines[0].lower().startswith(f"# {connector.metadata['name']}".lower()):
            errors.append(
                f"The connector name is not used as the main header in the documentation. Expected: '# {connector.metadata['name']}'"
            )
        return errors

    def check_sections(self, doc_lines: List[str]) -> List[str]:
        errors = []
        for expected_section in self.expected_sections:
            if expected_section.lower() not in doc_lines:
                errors.append(f"Connector documentation is missing a '{expected_section.replace('#', '').strip()}' section")
        return errors

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.documentation_file_path or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="Could not check documentation structure as the documentation file is missing.",
            )

        doc_lines = [line.lower() for line in connector.documentation_file_path.read_text().splitlines()]

        if not doc_lines:
            return self.fail(
                connector=connector,
                message="Documentation file is empty",
            )

        errors = []
        errors.extend(self.check_main_header(connector, doc_lines))
        errors.extend(self.check_sections(doc_lines))

        if errors:
            return self.fail(
                connector=connector,
                message=f"Connector documentation does not follow the guidelines: {'. '.join(errors)}",
            )
        return self.pass_(
            connector=connector,
            message="Documentation guidelines are followed",
        )


class CheckChangelogEntry(DocumentationCheck):
    name = "Connectors must have a changelog entry for each version"
    description = "Each new version of a connector must have a changelog entry defined in the user facing documentation in `./docs/integrations/<connector-type>s/<connector-name>.md`."

    def _run(self, connector: Connector) -> CheckResult:
        if connector.documentation_file_path is None or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="Could not check changelog entry as the documentation file is missing. Please create it.",
            )

        doc_lines = connector.documentation_file_path.read_text().splitlines()
        if not doc_lines:
            return self.fail(
                connector=connector,
                message="Documentation file is empty",
            )

        after_changelog = False
        entry_found = False
        for line in doc_lines:
            if "# changelog" in line.lower():
                after_changelog = True
            if after_changelog and connector.version in line:
                entry_found = True

        if not after_changelog:
            return self.fail(
                connector=connector,
                message="Connector documentation is missing a 'Changelog' section",
            )
        if not entry_found:
            return self.fail(
                connector=connector,
                message=f"Connectors must have a changelog entry for each version: changelog entry for version {connector.version} is missing in the documentation",
            )

        return self.pass_(connector=connector, message=f"Changelog entry found for version {connector.version}")


ENABLED_CHECKS = [
    CheckMigrationGuide(),
    CheckDocumentationExists(),
    # CheckDocumentationStructure(),  # Disabled as many are failing - we either need a big push or to block everyone. See https://github.com/airbytehq/airbyte/commit/4889e6e024d64ba0e353611f8fe67497b02de190#diff-3c73c6521bf819248b3d3d8aeab7cacfa4e8011f9890da93c77da925ece7eb20L262
    CheckChangelogEntry(),
]
