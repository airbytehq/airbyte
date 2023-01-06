import sys
import os
import os.path
import yaml
import re
from typing import Any, Dict, Text, List

CONNECTORS_PATH = "./airbyte-integrations/connectors/"
NORMALIZATION_PATH = "./airbyte-integrations/bases/base-normalization/"
DOC_PATH = "docs/integrations/"
SOURCE_DEFINITIONS_PATH = "./airbyte-config/init/src/main/resources/seed/source_definitions.yaml"
DESTINATION_DEFINITIONS_PATH = "./airbyte-config/init/src/main/resources/seed/destination_definitions.yaml"
IGNORE_LIST = [
    # Java
    "/src/test/","/src/test-integration/", "/src/testFixtures/",
    # Python
    "/integration_tests/", "/unit_tests/",
    # Common
    "acceptance-test-config.yml", "acceptance-test-docker.sh", ".md", ".dockerignore", ".gitignore", "requirements.txt"]
IGNORED_SOURCES = [
    re.compile("^source-e2e-test-cloud$"),
    re.compile("^source-mongodb$"),
    re.compile("^source-python-http-tutorial$"),
    re.compile("^source-relational-db$"),
    re.compile("^source-stock-ticker-api-tutorial$"),
    re.compile("source-jdbc$"),
    re.compile("^source-scaffold-.*$"),
    re.compile(".*-secure$"),
]
IGNORED_DESTINATIONS = [
    re.compile(".*-strict-encrypt$"),
    re.compile("^destination-dev-null$"),
    re.compile("^destination-scaffold-destination-python$"),
    re.compile("^destination-jdbc$")
]
COMMENT_TEMPLATE_PATH = ".github/comment_templates/connector_dependency_template.md"


def main():
    # Used git diff checks airbyte-integrations/ folder only
    # See .github/workflows/report-connectors-dependency.yml file
    git_diff_file_path = ' '.join(sys.argv[1:])

    if git_diff_file_path == None or git_diff_file_path == "":
        raise Exception("No changefile provided")

    # Get changed files
    changed_files = get_changed_files(git_diff_file_path)
    # Get changed modules. e.g. source-acceptance-test from airbyte-integrations/bases/
    # or destination-mysql from airbyte-integrations/connectors/
    changed_modules = get_changed_modules(changed_files)

    # Get all existing connectors
    all_connectors = get_all_connectors()

    # Getting all build.gradle file
    build_gradle_files = {}
    for connector in all_connectors:
        connector_path = CONNECTORS_PATH + connector + "/"
        build_gradle_files.update(get_gradle_file_for_path(connector_path))
    build_gradle_files.update(get_gradle_file_for_path(NORMALIZATION_PATH))

    # Try to find dependency in build.gradle file
    dependent_modules = list(set(get_dependent_modules(changed_modules, build_gradle_files)))

    # Create comment body to post on pull request
    if dependent_modules:
        write_report(dependent_modules)


def get_changed_files(path):
    changed_connectors_files = []
    with open(path) as file:
        for line in file:
            changed_connectors_files.append(line)
    return changed_connectors_files


def get_changed_modules(changed_files):
    changed_modules = []
    for changed_file in changed_files:
        # Check if this file should be ignored
        if not any(ignor in changed_file for ignor in IGNORE_LIST):
            split_changed_file = changed_file.split("/")
            changed_modules.append(split_changed_file[1] + ":" + split_changed_file[2])
    return list(set(changed_modules))


def get_all_connectors():
    walk = os.walk(CONNECTORS_PATH)
    return [connector for connector in next(walk)[1]]


def get_gradle_file_for_path(path: str) -> Dict[Text, Any]:
    if not path.endswith("/"):
        path = path + "/"
    build_gradle_file = find_file("build.gradle", path)
    module = path.split("/")[-2]
    return {module: build_gradle_file}


def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def get_dependent_modules(changed_modules, all_build_gradle_files):
    dependent_modules = []
    for changed_module in changed_modules:
        for module, gradle_file in all_build_gradle_files.items():
            if gradle_file is None:
                continue
            with open(gradle_file) as file:
                if changed_module in file.read():
                    dependent_modules.append(module)
    return dependent_modules


def get_connector_version(connector):
    with open(f"{CONNECTORS_PATH}/{connector}/Dockerfile") as f:
        for line in f:
            if "io.airbyte.version" in line:
                return line.split("=")[1].strip()


def get_connector_version_status(connector, version):
    if "strict-encrypt" not in connector:
        return f"`{version}`"
    if connector == "source-mongodb-strict-encrypt":
        base_variant_version = get_connector_version("source-mongodb-v2")
    else:
        base_variant_version = get_connector_version(connector.replace("-strict-encrypt", ""))
    if base_variant_version == version:
        return f"`{version}`"
    else:
        return f"❌ `{version}`<br/>(mismatch: `{base_variant_version}`)"


def get_connector_changelog_status(connector: str, version) -> str:
    type, name = connector.replace("-strict-encrypt", "").replace("-denormalized", "").split("-", 1)
    doc_path = f"{DOC_PATH}{type}s/{name}.md"

    if any(regex.match(connector) for regex in IGNORED_SOURCES):
        return "🔵<br/>(ignored)"
    if any(regex.match(connector) for regex in IGNORED_DESTINATIONS):
        return "🔵<br/>(ignored)"
    if not os.path.exists(doc_path):
        return "⚠<br/>(doc not found)"

    with open(doc_path) as f:
        after_changelog = False
        for line in f:
            if "# changelog" in line.lower():
                after_changelog = True
            if after_changelog and version in line:
                return "✅"

    return "❌<br/>(changelog missing)"


def as_bulleted_markdown_list(items):
    text = ""
    for item in items:
        text += f"- {item}\n"
    return text


def as_markdown_table_rows(connectors: List[str], definitions) -> str:
    text = ""
    for connector in connectors:
        version = get_connector_version(connector)
        version_status = get_connector_version_status(connector, version)
        changelog_status = get_connector_changelog_status(connector, version)
        definition = next((x for x in definitions if x["dockerRepository"].endswith(connector)), None)
        if any(regex.match(connector) for regex in IGNORED_SOURCES):
            publish_status = "🔵<br/>(ignored)"
        elif any(regex.match(connector) for regex in IGNORED_DESTINATIONS):
            publish_status = "🔵<br/>(ignored)"
        elif definition is None:
            publish_status = "⚠<br/>(not in seed)"
        elif definition["dockerImageTag"] == version:
            publish_status = "✅"
        else:
            publish_status = "❌<br/>(diff seed version)"
        text += f"| `{connector}` | {version_status} | {changelog_status} | {publish_status} |\n"
    return text


def get_status_summary(rows: str) -> str:
    if "❌" in rows:
        return "❌"
    elif "⚠" in rows:
        return "⚠"
    else:
        return "✅"


def write_report(depended_connectors):
    affected_sources = []
    affected_destinations = []
    affected_others = []
    for depended_connector in depended_connectors:
        if depended_connector.startswith("source"):
            affected_sources.append(depended_connector)
        elif depended_connector.startswith("destination"):
            affected_destinations.append(depended_connector)
        else:
            affected_others.append(depended_connector)

    with open(COMMENT_TEMPLATE_PATH, "r") as f:
        template = f.read()

    with open(SOURCE_DEFINITIONS_PATH, 'r') as stream:
        source_definitions = yaml.safe_load(stream)
    with open(DESTINATION_DEFINITIONS_PATH, 'r') as stream:
        destination_definitions = yaml.safe_load(stream)

    affected_sources.sort()
    affected_destinations.sort()
    affected_others.sort()

    source_rows = as_markdown_table_rows(affected_sources, source_definitions)
    destination_rows = as_markdown_table_rows(affected_destinations, destination_definitions)

    other_status_summary = "✅" if len(affected_others) == 0 else "👀"
    source_status_summary = get_status_summary(source_rows)
    destination_status_summary = get_status_summary(destination_rows)

    comment = template.format(
        source_open="open" if source_status_summary == "❌" else "closed",
        destination_open="open" if destination_status_summary == "❌" else "closed",
        source_status_summary=source_status_summary,
        destination_status_summary=destination_status_summary,
        other_status_summary=other_status_summary,
        source_rows=source_rows,
        destination_rows=destination_rows,
        others_rows=as_bulleted_markdown_list(affected_others),
        num_sources=len(affected_sources),
        num_destinations=len(affected_destinations),
        num_others=len(affected_others),
    )

    with open("comment_body.md", "w") as f:
        f.write(comment)


if __name__ == "__main__":
    main()
