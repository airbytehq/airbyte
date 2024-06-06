# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import re
import textwrap
from pathlib import Path
from threading import Thread
from typing import List

import requests
from connector_ops.utils import Connector, ConnectorLanguage  # type: ignore
from connectors_qa import consts
from connectors_qa.models import Check, CheckCategory, CheckResult
from connectors_qa.utils import (
    description_end_line_index,
    documentation_node,
    header_name,
    prepare_headers,
    prepare_lines_to_compare,
    reason_missing_titles,
    reason_titles_not_match,
    remove_not_required_step_headers,
    remove_step_from_heading,
    required_titles_from_spec,
)
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

    PREREQUISITES = "Prerequisites"
    HEADING = "heading"
    CREDENTIALS_KEYWORDS = ["account", "auth", "credentials", "access", "client"]
    CONNECTOR_SPECIFIC_HEADINGS = "<Connector-specific features>"

    def _get_template_headings(self, connector_name: str) -> tuple[tuple[str], tuple[str]]:
        """
        Headings in order to docs structure.
        """
        all_headings = (
            connector_name,
            "Prerequisites",
            "Setup guide",
            f"Set up {connector_name}",
            "For Airbyte Cloud:",
            "For Airbyte Open Source:",
            self.CONNECTOR_SPECIFIC_HEADINGS,
            f"Set up the {connector_name} connector in Airbyte",
            "For Airbyte Cloud:",
            "For Airbyte Open Source:",
            self.CONNECTOR_SPECIFIC_HEADINGS,
            "Supported sync modes",
            "Supported Streams",
            self.CONNECTOR_SPECIFIC_HEADINGS,
            "Performance considerations",
            "Data type map",
            "Limitations & Troubleshooting",
            self.CONNECTOR_SPECIFIC_HEADINGS,
            "Tutorials",
            "Changelog",
        )
        not_required_heading = (
            f"Set up the {connector_name} connector in Airbyte",
            "For Airbyte Cloud:",
            "For Airbyte Open Source:",
            self.CONNECTOR_SPECIFIC_HEADINGS,
            "Performance considerations",
            "Data type map",
            "Limitations & Troubleshooting",
            "Tutorials",
        )
        return all_headings, not_required_heading

    def _headings_description(self, connector_name: str) -> dict[str:Path]:
        """
        Headings with path to file with template description
        """
        descriptions_paths = {
            connector_name: Path(__file__).parent / "doc_templates/source.txt",
            "For Airbyte Cloud:": Path(__file__).parent / "doc_templates/for_airbyte_cloud.txt",
            "For Airbyte Open Source:": Path(__file__).parent / "doc_templates/for_airbyte_open_source.txt",
            "Supported sync modes": Path(__file__).parent / "doc_templates/supported_sync_modes.txt",
            "Tutorials": Path(__file__).parent / "doc_templates/tutorials.txt",
        }
        return descriptions_paths

    def check_main_header(self, connector: Connector, doc_lines: List[str]) -> List[str]:
        errors = []
        if not doc_lines[0].lower().startswith(f"# {connector.metadata['name']}".lower()):
            errors.append(
                f"The connector name is not used as the main header in the documentation. Expected: '# {connector.metadata['name']}'"
            )
        return errors

    def validate_links(self, docs_content) -> List[str]:
        valid_status_codes = [200, 403, 401, 405, 429, 503]  # we skip 4xx due to needed access
        links = re.findall("(https?://[^\s\`)]+)", docs_content)
        invalid_links = []
        threads = []

        def request_link(docs_link):
            try:
                response = requests.get(docs_link)
                if response.status_code not in valid_status_codes:
                    invalid_links.append(f"{docs_link} with {response.status_code} status code")
            except requests.exceptions.SSLError:
                pass

        for link in links:
            process = Thread(target=request_link, args=[link])
            process.start()
            threads.append(process)

        for process in threads:
            process.join(timeout=30)  # 30s timeout for process else link will be skipped
            process.is_alive()

        errors = []
        for link in invalid_links:
            errors.append(f"Link {link} is invalid in the connector documentation.")

        return errors

    def check_docs_structure(self, docs_content: str, connector_name: str) -> List[str]:
        """
        test_docs_structure gets all top-level headers from source documentation file and check that the order is correct.
        The order of the headers should follow our standard template https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw.
        _get_template_headings returns tuple of headers as in standard template and non-required headers that might nor be in the source docs.
        CONNECTOR_SPECIFIC_HEADINGS value in list of required headers that shows a place where should be a connector specific headers,
        which can be skipped as out of standard template and depends on connector.
        """
        errors = []

        heading_names = prepare_headers(docs_content)
        template_headings, non_required_heading = self._get_template_headings(connector_name)

        heading_names_len, template_headings_len = len(heading_names), len(template_headings)
        heading_names_index, template_headings_index = 0, 0

        while heading_names_index < heading_names_len and template_headings_index < template_headings_len:
            heading_names_value = heading_names[heading_names_index]
            template_headings_value = template_headings[template_headings_index]
            # check that template header is specific for connector and actual header should not be validated
            if template_headings_value == self.CONNECTOR_SPECIFIC_HEADINGS:
                # check that actual header is not in required headers, as required headers should be on a right place and order
                if heading_names_value not in template_headings:
                    heading_names_index += 1  # go to the next actual header as CONNECTOR_SPECIFIC_HEADINGS can be more than one
                    continue
                else:
                    # if actual header is required go to the next template header to validate actual header order
                    template_headings_index += 1
                    continue
            # strict check that actual header equals template header
            if heading_names_value == template_headings_value:
                # found expected header, go to the next header in template and actual headers
                heading_names_index += 1
                template_headings_index += 1
                continue
            # actual header != template header means that template value is not required and can be skipped
            if template_headings_value in non_required_heading:
                # found non-required header, go to the next template header to validate actual header
                template_headings_index += 1
                continue
            # any check is True, indexes didn't move to the next step
            errors.append(reason_titles_not_match(heading_names_value, template_headings_value, template_headings))
            return errors
        # indexes didn't move to the last required one, so some headers are missed
        if template_headings_index != template_headings_len:
            errors.append(reason_missing_titles(template_headings_index, template_headings))
            return errors

        return errors

    def check_prerequisites_section_has_descriptions_for_required_fields(
        self, actual_connector_spec: dict, connector_documentation: str, docs_path: str
    ) -> List[str]:
        errors = []
        if not actual_connector_spec:
            return errors

        node = documentation_node(connector_documentation)
        header_line_map = {header_name(n): n.map[1] for n in node if n.type == self.HEADING}
        headings = tuple(header_line_map.keys())

        if not header_line_map.get(self.PREREQUISITES):
            return [f"Documentation does not have {self.PREREQUISITES} section."]

        prereq_start_line = header_line_map[self.PREREQUISITES]
        prereq_end_line = description_end_line_index(self.PREREQUISITES, headings, header_line_map)

        with open(docs_path, "r") as docs_file:
            prereq_content_lines = docs_file.readlines()[prereq_start_line:prereq_end_line]
            # adding real character to avoid accidentally joining lines into a wanted title.
            prereq_content = "|".join(prereq_content_lines).lower()
            spec = actual_connector_spec.get("connectionSpecification") or actual_connector_spec.get("connection_specification")
            required_titles, has_credentials = required_titles_from_spec(spec)

            for title in required_titles:
                if title not in prereq_content:
                    errors.append(
                        f"Required '{title}' field is not in {self.PREREQUISITES} section "
                        f"or title in spec doesn't match name in the docs."
                    )

            if has_credentials:
                # credentials has specific check for keywords as we have a lot of way how to describe this step
                credentials_validation = [k in prereq_content for k in self.CREDENTIALS_KEYWORDS]
                if True not in credentials_validation:
                    errors.append(f"Required description for 'credentials' field is not in {self.PREREQUISITES} section.")

            return errors

    def check_docs_descriptions(self, docs_path: str, connector_documentation: str, connector_name: str) -> List[str]:
        errors = []
        template_descriptions = self._headings_description(connector_name)

        node = documentation_node(connector_documentation)
        header_line_map = {header_name(n): n.map[1] for n in node if n.type == self.HEADING}
        actual_headings = tuple(header_line_map.keys())

        for heading, description in template_descriptions.items():
            if heading in actual_headings:

                description_start_line = header_line_map[heading]
                description_end_line = description_end_line_index(heading, actual_headings, header_line_map)

                with open(docs_path, "r") as docs_file, open(description, "r") as template_file:

                    docs_description_content = docs_file.readlines()[description_start_line:description_end_line]
                    template_description_content = template_file.readlines()

                    for d, t in zip(docs_description_content, template_description_content):
                        d, t = prepare_lines_to_compare(connector_name, d, t)
                        if d != t:
                            errors.append(f"Description for '{heading}' does not follow structure.\nExpected: {t} Actual: {d}")

        return errors

    def _run(self, connector: Connector) -> CheckResult:
        connector_type, sl_level = connector.connector_type, connector.ab_internal_sl
        if connector_type == "source" and sl_level >= 300 and connector.language != ConnectorLanguage.JAVA:

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

            docs_content = connector.documentation_file_path.read_text().rstrip()

            errors = []
            errors.extend(self.check_main_header(connector, doc_lines))
            errors.extend(self.validate_links(docs_content))
            errors.extend(self.check_docs_structure(docs_content, connector.name_from_metadata))
            errors.extend(
                self.check_prerequisites_section_has_descriptions_for_required_fields(
                    connector.connector_spec, docs_content, connector.documentation_file_path
                )
            )
            errors.extend(self.check_docs_descriptions(connector.documentation_file_path, docs_content, connector.name_from_metadata))

            if errors:
                return self.fail(
                    connector=connector,
                    message=f"Connector documentation does not follow the guidelines: {'. '.join(errors)}",
                )
            return self.pass_(
                connector=connector,
                message="Documentation guidelines are followed",
            )

        return self.skip(
            connector=connector,
            reason="Check does not apply for sources with sl < 300 or/and java sources",
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
    CheckDocumentationStructure(),
    CheckChangelogEntry(),
]
