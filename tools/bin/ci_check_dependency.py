import sys
import os
import os.path

CONNECTOR_FOLDER = "airbyte-integrations/connectors/"
CONNECTOR_PATH = "./airbyte-integrations/connectors/"
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
            with open(gradle_file) as file:
                if changed_module in file.read():
                    depended_connectors.append(connector)
    return depended_connectors


def as_bulleted_markdown_list(items):
    text = ""
    for item in items:
        text += f"- {item}\n"
    return text


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

    others_md = ""
    if affected_others:
        others_md += "The following were also affected:\n"
        others_md += as_bulleted_markdown_list(affected_others)

    comment = template.format(
        sources=as_bulleted_markdown_list(affected_sources),
        destinations=as_bulleted_markdown_list(affected_destinations),
        others=others_md,
        num_sources=len(affected_sources),
        num_destinations=len(affected_destinations)
    )

    with open("comment_body.md", "w") as f:
        f.write(comment)


if __name__ == "__main__":
    main()
