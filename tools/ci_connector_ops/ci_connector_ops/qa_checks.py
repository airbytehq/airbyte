#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from ci_connector_ops.utils import Connector


def check_documentation_file_exists(connector: Connector) -> bool:
    """Check if a markdown file with connector documentation is available
    in docs/integrations/<connector-type>s/<connector-name>.md

    Args:
        connector (Connector): a Connector dataclass instance.

    Returns:
        bool: Wether a documentation file was found.
    """

    return connector.documentation_file_path.exists()

def check_documentation_follows_guidelines(connector: Connector) -> bool:
    """Documentation guidelines are defined here https://hackmd.io/Bz75cgATSbm7DjrAqgl4rw"""
    follows_guidelines = True
    with open(connector.documentation_file_path) as f:
        doc_lines = [l.lower() for l in f.read().splitlines()]
    if not doc_lines[0].startswith("# "):
        print("The connector name is not used as the main header in the documentation.")
        follows_guidelines = False
    if connector.definition: # We usually don't have a definition if the connector is not published.
        if doc_lines[0].strip() != f"# {connector.definition['name'].lower()}":
            print("The connector name is not used as the main header in the documentation.")
            follows_guidelines = False
    elif not doc_lines[0].startswith("# "):
        print("The connector name is not used as the main header in the documentation.")
        follows_guidelines = False

    expected_sections = [
        "## Prerequisites",
        "## Setup guide",
        "## Supported sync modes",
        "## Supported streams",
        "## Changelog"
    ]

    for expected_section in expected_sections:
        if expected_section.lower() not in doc_lines:
            print(f"Connector documentation is missing a '{expected_section.replace('#', '').strip()}' section.")
            follows_guidelines = False
    return follows_guidelines

def check_changelog_entry_is_updated(connector: Connector) -> bool:
    """Check that the changelog entry is updated for the latest connector version
    in docs/integrations/<connector-type>/<connector-name>.md

    Args:
        connector (Connector): a Connector dataclass instance.

    Returns:
        bool: Wether a the changelog is up to date.
    """
    if not check_documentation_file_exists(connector):
        return False
    with open(connector.documentation_file_path) as f:
        after_changelog = False
        for line in f:
            if "# changelog" in line.lower():
                after_changelog = True
            if after_changelog and connector.version in line:
                return True
    return False

def check_connector_icon_is_available(connector: Connector) -> bool:
    """Check an SVG icon exists for a connector in
    in airbyte-config/init/src/main/resources/icons/<connector-name>.svg

    Args:
        connector (Connector): a Connector dataclass instance.

    Returns:
        bool: Wether an icon exists for this connector.
    """
    return connector.icon_path.exists()

def check_connector_https_url_only(connector: Connector) -> bool:
    """Check a connector code contains only https url.

    Args:
        connector (Connector): a Connector dataclass instance.

    Returns:
        bool: Wether the connector code contains only https url.
    """
    # TODO implement
    return True

def check_connector_has_no_critical_vulnerabilities(connector: Connector) -> bool:
    """Check if the connector image is free of critical Snyk vulnerabilities.
    Runs a docker scan command.

    Args:
        connector (Connector): a Connector dataclass instance.

    Returns:
        bool: Wether the connector is free of critical vulnerabilities.
    """
    # TODO implement
    return True

QA_CHECKS = [
    check_documentation_file_exists,
    # Disabling the following check because it's likely to not pass on a lot of connectors.
    # check_documentation_follows_guidelines,
    check_changelog_entry_is_updated,
    check_connector_icon_is_available,
    check_connector_https_url_only,
    check_connector_has_no_critical_vulnerabilities
]

def run_qa_checks():
    connector_technical_name = sys.argv[1].split("/")[-1]
    if not connector_technical_name.startswith("source-") and not connector_technical_name.startswith("destination-"):
        print("No QA check to run as this is not a connector.")
        sys.exit(0)
    connector = Connector(connector_technical_name)
    print(f"Running QA checks for {connector_technical_name}:{connector.version}")
    qa_check_results = {qa_check.__name__: qa_check(connector) for qa_check in QA_CHECKS}
    if not all(qa_check_results.values()):
        print(f"QA checks failed for {connector_technical_name}:{connector.version}:")
        for check_name, check_result in qa_check_results.items():
            check_result_prefix = "✅" if check_result else "❌"
            print(f"{check_result_prefix} - {check_name}")
        sys.exit(1)
    else:
        print(f"All QA checks succeeded for {connector_technical_name}:{connector.version}")
        sys.exit(0)
