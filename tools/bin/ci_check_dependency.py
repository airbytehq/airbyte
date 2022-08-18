import sys
import os
import os.path
import logging

LOGGING_FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
CONNECTOR_FOLDER = "airbyte-integrations/connectors/"
CONNECTOR_PATH = "./airbyte-integrations/connectors/"


def main():
    # home_directory = os.getenv("HOME")
    # logging.info(f"HOME directory: {home_directory}")
    git_diff_file_path = ' '.join(sys.argv[1:])
    # logging.info(f"git diff files path {git_diff_file_path}")

    # Get changed connectors
    changed_connectors_files = get_changed_connectors(git_diff_file_path)
    # logging.info(f"Changed connectors  {changed_connectors_files}")

    # Get all connectors
    all_connectors = get_all_connectors()
    # logging.info(f"Found {len(all_connectors)} connectors to check")

    # getting all build.gradle file
    all_build_gradle_files = get_connectors_gradle_files(all_connectors)
    # logging.info(f"Found {len(all_build_gradle_files)} build.gradle files")

    # Checking build.gradle filse
    depended_connectors = list(set(get_depended_connectors(changed_connectors_files, all_build_gradle_files)))
    # logging.info(f"Make sure to run corresponding integration tests: {depended_connectors}")

    write_report(depended_connectors)


def get_changed_connectors(path):
    changed_connectors_files = []
    with open(path) as file:
        for line in file:
            if CONNECTOR_FOLDER in line:
                changed_connectors_files.append(line.split("/")[2])
    return list(set(changed_connectors_files))


def get_all_connectors():
    walk = os.walk(CONNECTOR_PATH)
    return [connector for connector in next(walk)[1]]


def get_connectors_gradle_files(all_connectors):
    all_build_gradle_files = {}
    for connector in all_connectors:
        build_gradle_path = CONNECTOR_PATH + connector + "/"
        build_gradle_file = findFile("build.gradle", build_gradle_path)
        all_build_gradle_files[connector] = build_gradle_file
    return all_build_gradle_files


def findFile(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def get_depended_connectors(changed_connectors_files, all_build_gradle_files):
    depended_connectors = []
    for changed_connector in changed_connectors_files:
        # logging.info(f"Trying to find dependency for: {changed_connector}")
        for connector, gradle_file in all_build_gradle_files.items():
            with open(gradle_file) as f:
                if changed_connector in f.read():
                    # logging.info(f"Dependency found in: {connector}")
                    depended_connectors.append(connector)
    return depended_connectors


def write_report(depended_connectors):
    empty_report_test = []
    for depended_connector in empty_report_test:
        print("- " + depended_connector)


if __name__ == "__main__":
    logging.basicConfig(format=LOGGING_FORMAT, level=logging.INFO)
    main()
