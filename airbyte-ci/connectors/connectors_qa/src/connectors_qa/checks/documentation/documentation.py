# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import abc
import textwrap
from difflib import get_close_matches, ndiff
from threading import Thread
from typing import List

import requests  # type: ignore
from connector_ops.utils import Connector, ConnectorLanguage  # type: ignore
from pydash.objects import get  # type: ignore

from connectors_qa.models import Check, CheckCategory, CheckResult

from .helpers import (
    generate_description,
    prepare_changelog_to_compare,
    prepare_headers,
    reason_missing_titles,
    reason_titles_not_match,
    replace_connector_specific_urls_from_section,
    required_titles_from_spec,
)
from .models import DocumentationContent, TemplateContent


class DocumentationCheck(Check):
    category = CheckCategory.DOCUMENTATION
    applies_to_connector_ab_internal_sl = 100


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


class CheckDocumentationContent(DocumentationCheck):
    """
    For now, we check documentation structure for sources with sl >= 300.
    """

    applies_to_connector_languages = [ConnectorLanguage.PYTHON, ConnectorLanguage.LOW_CODE]
    applies_to_connector_ab_internal_sl = 300
    applies_to_connector_types = ["source"]


class CheckDocumentationLinks(CheckDocumentationContent):
    name = "Links used in connector documentation are valid"
    description = "The user facing connector documentation should update invalid links in connector documentation. For links that are used as example and return 404 status code, use `example: ` before link to skip it."

    def validate_links(self, connector: Connector) -> List[str]:
        errors = []
        threads = []

        def request_link(docs_link: str) -> None:
            try:
                response = requests.get(docs_link)
                if response.status_code == 404:
                    errors.append(f"{docs_link} with {response.status_code} status code")
            except requests.exceptions.SSLError:
                pass
            except requests.exceptions.ConnectionError:
                pass

        for link in DocumentationContent(connector=connector).links:
            process = Thread(target=request_link, args=[link])
            process.start()
            threads.append(process)

        for process in threads:
            process.join(timeout=30)  # 30s timeout for process else link will be skipped
            process.is_alive()

        return errors

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.documentation_file_path or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="Could not check documentation links as the documentation file is missing.",
            )

        if not connector.documentation_file_path.read_text().rstrip():
            return self.fail(
                connector=connector,
                message="Documentation file is empty",
            )

        errors = self.validate_links(connector)
        if errors:
            return self.fail(
                connector=connector,
                message=f"Connector documentation uses invalid links: {', '.join(errors)}",
            )
        return self.pass_(
            connector=connector,
            message="Documentation links are valid",
        )


class CheckDocumentationHeadersOrder(CheckDocumentationContent):
    name = "Connectors documentation headers structure, naming and order follow our guidelines"

    CONNECTOR_SPECIFIC_HEADINGS = "CONNECTOR_SPECIFIC_FEATURES"

    @property
    def description(self) -> str:
        ordered_headers = TemplateContent("CONNECTOR_NAME_FROM_METADATA").headers_with_tag()
        not_required_headers = [
            "Set up the CONNECTOR_NAME_FROM_METADATA connector in Airbyte",
            "For Airbyte Cloud: (as subtitle of Set up CONNECTOR_NAME_FROM_METADATA)",
            "For Airbyte Open Source: (as subtitle of Set up CONNECTOR_NAME_FROM_METADATA)",
            self.CONNECTOR_SPECIFIC_HEADINGS + " (but this headers should be on a right place according to expected order)",
            "Performance considerations",
            "Data type map",
            "Limitations & Troubleshooting",
            "Tutorials",
        ]

        return generate_description(
            "documentation_headers_check_description.md.j2",
            {"ordered_headers": ordered_headers, "not_required_headers": not_required_headers},
        )

    def get_not_required_headers(self, connector_name: str) -> list[str]:
        not_required = [
            f"Set up the {connector_name} connector in Airbyte",
            "For Airbyte Cloud:",
            "For Airbyte Open Source:",
            self.CONNECTOR_SPECIFIC_HEADINGS,
            "Performance considerations",
            "Data type map",
            "Limitations & Troubleshooting",
            "Tutorials",
        ]
        return not_required

    def check_headers(self, connector: Connector) -> List[str]:
        """
        test_docs_structure gets all top-level headers from source documentation file and check that the order is correct.
        The order of the headers should follow our standard template connectors_qa/checks/documentation/templates/template.md.j2,
        which based on https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw.
        _get_template_headings returns tuple of headers as in standard template and non-required headers that might nor be in the source docs.
        CONNECTOR_SPECIFIC_HEADINGS value in list of required headers that shows a place where should be a connector specific headers,
        which can be skipped as out of standard template and depends on connector.
        """
        errors = []

        actual_headers = prepare_headers(DocumentationContent(connector=connector).headers)
        expected_headers = TemplateContent(connector.name_from_metadata).headers
        not_required_headers = self.get_not_required_headers(connector.name_from_metadata)

        actual_header_len, expected_len = len(actual_headers), len(expected_headers)
        actual_header_index, expected_header_index = 0, 0

        while actual_header_index < actual_header_len and expected_header_index < expected_len:
            actual_header = actual_headers[actual_header_index]
            expected_header = expected_headers[expected_header_index]
            # check that template header is specific for connector and actual header should not be validated
            if expected_header == self.CONNECTOR_SPECIFIC_HEADINGS:
                # check that actual header is not in required headers, as required headers should be on a right place and order
                if actual_header not in expected_headers:
                    actual_header_index += 1  # go to the next actual header as CONNECTOR_SPECIFIC_HEADINGS can be more than one
                    continue
                else:
                    # if actual header is required go to the next template header to validate actual header order
                    expected_header_index += 1
                    continue
            # strict check that actual header equals template header
            if actual_header == expected_header:
                # found expected header, go to the next header in template and actual headers
                actual_header_index += 1
                expected_header_index += 1
                continue
            # actual header != template header means that template value is not required and can be skipped
            if expected_header in not_required_headers:
                # found non-required header, go to the next template header to validate actual header
                expected_header_index += 1
                continue
            # any check is True, indexes didn't move to the next step
            errors.append(reason_titles_not_match(actual_header, expected_header, expected_headers))
            return errors
        # indexes didn't move to the last required one, so some headers are missed
        if expected_header_index != expected_len:
            errors.append(reason_missing_titles(expected_header_index, expected_headers, not_required_headers))
            return errors

        return errors

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.documentation_file_path or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="Could not check documentation structure as the documentation file is missing.",
            )

        if not connector.documentation_file_path.read_text():
            return self.fail(
                connector=connector,
                message="Documentation file is empty",
            )

        errors = self.check_headers(connector)

        if errors:
            return self.fail(
                connector=connector,
                message=f"Documentation headers ordering/naming doesn't follow guidelines:\n {'. '.join(errors)}",
            )
        return self.pass_(
            connector=connector,
            message="Documentation guidelines are followed",
        )


class CheckPrerequisitesSectionDescribesRequiredFieldsFromSpec(CheckDocumentationContent):
    name = "Prerequisites section of the documentation describes all required fields from specification"
    description = (
        "The user facing connector documentation should update `Prerequisites`"
        " section with description for all required fields from source specification. "
        "Having described all required fields in a one place helps Airbyte users easily set up the source connector. \n"
        "If spec has required credentials/access_token/refresh_token etc, "
        'check searches for one of ["account", "auth", "credentials", "access", "client"] words. '
        "No need to add credentials/access_token/refresh_token etc to the section"
    )

    PREREQUISITES = "Prerequisites"
    CREDENTIALS_KEYWORDS = ["account", "auth", "credentials", "access", "client"]

    def check_prerequisites(self, connector: Connector) -> List[str]:
        actual_connector_spec = connector.connector_spec_file_content
        if not actual_connector_spec:
            return []

        documentation = DocumentationContent(connector=connector)
        if self.PREREQUISITES not in documentation.headers:
            return [f"Documentation does not have {self.PREREQUISITES} section."]

        section_content = documentation.section(self.PREREQUISITES)
        if section_content is None:
            return [f"Documentation {self.PREREQUISITES} section is empty"]

        if len(section_content) > 1:
            return [f"Documentation has more than one {self.PREREQUISITES} section. Please check it."]

        section_text = section_content[0].lower()

        spec = actual_connector_spec.get("connectionSpecification") or actual_connector_spec.get("connection_specification")
        required_titles, has_credentials = required_titles_from_spec(spec)  # type: ignore

        missing_fields: List[str] = []
        for title in required_titles:
            if title.lower() not in section_text:
                missing_fields.append(title)

        if has_credentials:
            credentials_validation = [k in section_text for k in self.CREDENTIALS_KEYWORDS]
            if True not in credentials_validation:
                missing_fields.append("credentials")

        return missing_fields

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.documentation_file_path or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="Could not check documentation structure as the documentation file is missing.",
            )

        if not connector.documentation_file_path.read_text():
            return self.fail(
                connector=connector,
                message="Documentation file is empty",
            )

        # check_prerequisites uses spec content from file, not from spec command,
        # which possible can lead to incorrect testing, for now it works for connectors with sl>=300.
        # But if someone faced with unexpected behavior of this test it's better to disable it.

        errors = self.check_prerequisites(connector)

        if errors:
            return self.fail(
                connector=connector,
                message=f"Missing descriptions for required spec fields: {'. '.join(errors)}",
            )
        return self.pass_(
            connector=connector,
            message="All required fields from spec are present in the connector documentation",
        )


class CheckSection(CheckDocumentationContent):
    required = True
    expected_section_index = 0

    @property
    def name(self) -> str:
        return f"'{self.header}' section of the documentation follows our guidelines"

    @property
    def description(self) -> str:
        templates = TemplateContent("CONNECTOR_NAME_FROM_METADATA").section(self.header)
        if templates is None:
            template = ""  # Provide default empty template if section is missing
        elif len(templates) > 1:
            template = templates[1]
        else:
            template = templates[0]

        return generate_description("section_content_description.md.j2", {"header": self.header, "template": template})

    @property
    @abc.abstractmethod
    def header(self) -> str:
        """The name of header for validating content"""

    def check_section(self, connector: Connector) -> List[str]:
        documentation = DocumentationContent(connector=connector)

        if self.header not in documentation.headers:
            if self.required:
                return [f"Documentation does not have {self.header} section."]
            return []

        errors = []

        expected = TemplateContent(connector.name_from_metadata).section(self.header)[self.expected_section_index]  # type: ignore
        actual_contents = documentation.section(self.header)
        if actual_contents is None:
            return [f"Documentation {self.header} section is empty"]

        actual_contents = [c[: len(expected)] if len(c) > len(expected) else c for c in actual_contents]

        close_matches = get_close_matches(expected, actual_contents)
        if not close_matches:
            return [f"Please review your {self.header} section, unable to find the expected content:\n{expected}"]

        actual = close_matches[0]
        if actual != expected:
            errors = list(ndiff(actual.splitlines(keepends=True), expected.splitlines(keepends=True)))

        return errors

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.documentation_file_path or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="Could not check documentation structure as the documentation file is missing.",
            )

        if not connector.documentation_file_path.read_text():
            return self.fail(
                connector=connector,
                message="Documentation file is empty",
            )

        errors = self.check_section(connector)

        if errors:
            return self.fail(
                connector=connector,
                message=f"Connector {self.header} section content does not follow standard template:\n{''.join(errors)}",
            )
        return self.pass_(
            connector=connector,
            message="Documentation guidelines are followed",
        )


class CheckSourceSectionContent(CheckDocumentationContent):
    name = "Main Source Section of the documentation follows our guidelines"

    expected_section_index = 0

    @property
    def description(self) -> str:
        template = TemplateContent("CONNECTOR_NAME_FROM_METADATA").section("CONNECTOR_NAME_FROM_METADATA")
        if template is None:
            template_content = ""  # Provide default empty template if section is missing
        else:
            template_content = template[0]  # type: ignore

        return generate_description(
            "section_content_description.md.j2", {"header": "CONNECTOR_NAME_FROM_METADATA", "template": template_content}
        )

    def check_source_follows_template(self, connector: Connector) -> List[str]:
        documentation = DocumentationContent(connector=connector)

        if connector.name_from_metadata not in documentation.headers:
            return [f"Documentation does not have {connector.name_from_metadata} section."]

        errors = []

        header = connector.name_from_metadata

        expected_content = TemplateContent(header).section(header)
        if expected_content is None:
            return [f"Template {header} section is empty"]

        actual_contents = DocumentationContent(connector).section(header)
        if actual_contents is None:
            return [f"Documentation {header} section is empty"]

        expected = expected_content[self.expected_section_index]  # type: ignore

        if len(actual_contents) > 1:
            return [f"Expected only one header {header}. Please rename duplicate."]

        actual = replace_connector_specific_urls_from_section(actual_contents[0])

        if actual is None:
            return [f"Documentation {header} section is empty"]

        # actual connector doc can have imports etc. in this section
        if expected not in actual:
            errors = list(ndiff(actual.splitlines(keepends=True), expected.splitlines(keepends=True)))

        return errors

    def _run(self, connector: Connector) -> CheckResult:
        if not connector.documentation_file_path or not connector.documentation_file_path.exists():
            return self.fail(
                connector=connector,
                message="Could not check documentation structure as the documentation file is missing.",
            )

        if not connector.documentation_file_path.read_text():
            return self.fail(
                connector=connector,
                message="Documentation file is empty",
            )

        errors = self.check_source_follows_template(connector)

        if errors:
            return self.fail(
                connector=connector,
                message=f"Connector {connector.name_from_metadata} section content does not follow standard template:{''.join(errors)}",
            )
        return self.pass_(
            connector=connector,
            message="Documentation guidelines are followed",
        )


class CheckForAirbyteCloudSectionContent(CheckSection):
    header = "For Airbyte Cloud:"
    expected_section_index = 1


class CheckForAirbyteOpenSectionContent(CheckSection):
    header = "For Airbyte Open Source:"
    expected_section_index = 1


class CheckSupportedSyncModesSectionContent(CheckSection):
    header = "Supported sync modes"


class CheckTutorialsSectionContent(CheckSection):
    header = "Tutorials"
    required = False


class CheckChangelogSectionContent(CheckSection):
    header = "Changelog"

    def check_section(self, connector: Connector) -> List[str]:
        documentation = DocumentationContent(connector=connector)

        if self.header not in documentation.headers:
            if self.required:
                return [f"Documentation does not have {self.header} section."]
            return []

        errors = []

        expected = TemplateContent(connector.name_from_metadata).section(self.header)[self.expected_section_index]  # type: ignore
        actual_contents = documentation.section(self.header)
        if actual_contents is None:
            return [f"Documentation {self.header} section is empty"]

        if len(actual_contents) > 1:
            return [f"Documentation has more than one {self.header} section. Please check it."]

        actual = prepare_changelog_to_compare(actual_contents[0])[: len(expected)]
        if actual != expected:
            errors = list(ndiff(actual.splitlines(keepends=True), expected.splitlines(keepends=True)))

        return errors


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
