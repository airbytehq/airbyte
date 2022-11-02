import sys
import os
import os.path
import yaml

CONNECTOR_PATH = "./airbyte-integrations/connectors/"
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
COMMENT_TEMPLATE_PATH = ".github/comment_templates/connector_dependency_template.md"


def main():
    # Used git diff checks airbyte-integrations/ folder only
    # See .github/workflows/report-connectors-dependency.yml file
    git_diff_file_path = ' '.join(sys.argv[1:])

    # Get changed files
    changed_files = get_changed_files(git_diff_file_path)
    # Get changed modules. e.g. source-acceptance-test from airbyte-integrations/bases/
    # or destination-mysql from airbyte-integrations/connectors/
    changed_modules = get_changed_modules(changed_files)

    # Get all existing connectors
    all_connectors = get_all_connectors()

    # Getting all build.gradle file
    all_build_gradle_files = get_connectors_gradle_files(all_connectors)

    # Try to find dependency in build.gradle file
    depended_connectors = list(set(get_depended_connectors(changed_modules, all_build_gradle_files)))

    # Create comment body to post on pull request
    if depended_connectors:
        write_report(depended_connectors)


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
    walk = os.walk(CONNECTOR_PATH)
    return [connector for connector in next(walk)[1]]


def get_connectors_gradle_files(all_connectors):
    all_build_gradle_files = {}
    for connector in all_connectors:
        build_gradle_path = CONNECTOR_PATH + connector + "/"
        build_gradle_file = find_file("build.gradle", build_gradle_path)
        all_build_gradle_files[connector] = build_gradle_file
    return all_build_gradle_files


def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def get_depended_connectors(changed_modules, all_build_gradle_files):
    depended_connectors = []
    for changed_module in changed_modules:
        for connector, gradle_file in all_build_gradle_files.items():
            if gradle_file is None:
                continue
            with open(gradle_file) as file:
                if changed_module in file.read():
                    depended_connectors.append(connector)
    return depended_connectors


def get_connector_version(connector):
    with open(f"{CONNECTOR_PATH}/{connector}/Dockerfile") as f:
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


def get_connector_changelog_status(connector, version):
    type, name = connector.replace("-strict-encrypt", "").split("-", 1)
    doc_path = f"{DOC_PATH}{type}s/{name}.md"
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


def as_markdown_table_rows(connectors, definitions):
    text = ""
    for connector in connectors:
        version = get_connector_version(connector)
        version_status = get_connector_version_status(connector, version)
        changelog_status = get_connector_changelog_status(connector, version)
        definition = next((x for x in definitions if x["dockerRepository"].endswith(connector)), None)
        if definition is None:
            publish_status = "⚠<br/>(not in seed)"
        elif definition["dockerImageTag"] == version:
            publish_status = "✅"
        else:
            publish_status = "❌<br/>(diff seed version)"
        text += f"| `{connector}` | {version_status} | {changelog_status} | {publish_status} |\n"
    return text


def get_status_summary(rows):
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

    source_definitions = []
    destination_definitions = []
    with open(SOURCE_DEFINITIONS_PATH, 'r') as stream:
        source_definitions = yaml.safe_load(stream)
    with open(DESTINATION_DEFINITIONS_PATH, 'r') as stream:
        destination_definitions = yaml.safe_load(stream)

    others_md = ""
    if affected_others:
        others_md += "The following were also affected:\n"
        others_md += as_bulleted_markdown_list(affected_others)

    affected_sources.sort()
    affected_destinations.sort()
    affected_others.sort()

    source_rows = as_markdown_table_rows(affected_sources, source_definitions)
    destination_rows = as_markdown_table_rows(affected_destinations, destination_definitions)

    source_status_summary = get_status_summary(source_rows)
    destination_status_summary = get_status_summary(destination_rows)

    comment = template.format(
        source_open="open" if source_status_summary == "❌" else "closed",
        destination_open="open" if destination_status_summary == "❌" else "closed",
        source_status_summary=source_status_summary,
        destination_status_summary=destination_status_summary,
        source_rows=source_rows,
        destination_rows=destination_rows,
        others=others_md,
        num_sources=len(affected_sources),
        num_destinations=len(affected_destinations)
    )

    with open("comment_body.md", "w") as f:
        f.write(comment)


if __name__ == "__main__":
    main()
