import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

INTELLIJ_VERSION_FLAG = "-intellij-version"


def is_environment_in_jdk_table(environment_name, table):
    for elem in table:
        for subelem in elem:
            attribute = subelem.attrib
            if attribute.get("value") == environment_name:
                return True
    return False


def add_venv_to_xml_root(module: str, module_full_path: str, xml_root):
    """
    Add a new entry for the virtual environment to IntelliJ's list of known interpreters
    """
    path_to_lib = f"{module_full_path}/.venv/lib/"

    python_version = os.listdir(path_to_lib)[0]
    environment_name = f"{python_version.capitalize()} ({module})"

    table = xml_root.find("component")

    if is_environment_in_jdk_table(environment_name, table):
        print(f"{environment_name} already exists. Skipping...")
        return

    jdk_node = ET.SubElement(table, 'jdk', {"version": "2"})

    ET.SubElement(jdk_node, "name", {"value": environment_name})
    ET.SubElement(jdk_node, "type", {"value": "Python SDK"})
    ET.SubElement(jdk_node, "version", {"value": f"{python_version}"})
    ET.SubElement(jdk_node, "homePath",
                  {"value": f"{module_full_path}/.venv/bin/python"})

    roots = ET.SubElement(jdk_node, "roots")
    annotationsPath = ET.SubElement(roots, "annotationsPath")
    ET.SubElement(annotationsPath, "root", {"type": "composite"})

    classPath = ET.SubElement(roots, "classPath")
    classPathRoot = ET.SubElement(classPath, "root", {"type": "composite"})

    ET.SubElement(classPathRoot, "root", {"url":
                                              f"file://{path_to_lib}{python_version}/site-packages",
                                          "type": "simple"
                                          })


def get_output_path(input_path, output_path):
    if output_path is None:
        return input_path
    else:
        return output_path


def get_input_path(input_from_args, version, home_directory):
    if input_from_args is not None:
        return input_from_args
    else:
        path_to_intellij_settings = f"{home_directory}/Library/Application Support/JetBrains/"
        walk = os.walk(path_to_intellij_settings)
        intellij_versions = [version for version in next(walk)[1] if version != "consentOptions"]
        if version in intellij_versions:
            intellij_version_to_update = version
        elif len(intellij_versions) == 1:
            intellij_version_to_update = intellij_versions[0]
        else:
            raise RuntimeError(
                f"Please select which version of Intellij to update with the `{INTELLIJ_VERSION_FLAG}` flag. Options are: {intellij_versions}")
        return f"{path_to_intellij_settings}{intellij_version_to_update}/options/jdk.table.xml"


def module_has_requirements_file(module):
    path_to_module = f"{path_to_connectors}{module}"
    path_to_requirements_file = f"{path_to_module}/requirements.txt"
    return os.path.exists(path_to_requirements_file)


def get_default_airbyte_path():
    path_to_script = os.path.dirname(__file__)
    relative_path_to_airbyte_root = f"{path_to_script}/../.."
    return os.path.realpath(relative_path_to_airbyte_root)


def create_parser():
    parser = argparse.ArgumentParser(description="Prepare Python virtual environments for Python connectors")
    actions_group = parser.add_argument_group("actions")
    actions_group.add_argument("--install-venv", action="store_true",
                               help="Create virtual environment and install the module's dependencies")
    actions_group.add_argument("--update-intellij", action="store_true", help="Add interpreter to IntelliJ's list of known interpreters")

    parser.add_argument("-airbyte", default=get_default_airbyte_path(),
                        help="Path to Airbyte root directory")

    modules_group = parser.add_mutually_exclusive_group(required=True)
    modules_group.add_argument("-modules", nargs="?", help="Comma separated list of modules to add (eg source-strava,source-stripe)")
    modules_group.add_argument("--all-modules", action="store_true", help="Select all Python connector modules")

    group = parser.add_argument_group("Update intelliJ")

    group.add_argument("-input", help="Path to input IntelliJ's jdk table")
    group.add_argument("-output", help="Path to output jdk table")
    group.add_argument(INTELLIJ_VERSION_FLAG, help="IntelliJ version to update (Only required if multiple versions are installed)")

    return parser


def parse_args(args):
    parser = create_parser()
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    if not args.install_venv and not args.update_intellij:
        print("No action requested. Add -h for help")
        exit(-1)
    path_to_connectors = f"{args.airbyte}/airbyte-integrations/connectors/"

    if args.all_modules:
        print(path_to_connectors)
        modules = next(os.walk(path_to_connectors))[1]
    else:
        modules = args.modules.split(",")

    modules = [m for m in modules if module_has_requirements_file(m)]

    if args.install_venv:
        errors = []
        modules_installed = []
        for module in modules:
            result = subprocess.run(["tools/bin/setup_connector_venv.sh", module, sys.executable], check=False)
            if result.returncode == 0:
                modules_installed.append(module)
            else:
                errors.append(module)
        if len(modules_installed) > 0:
            print(f"Successfully installed virtual environment for {modules_installed}")
        if len(errors) > 0:
            print(f"Failed to install virtual environment for {errors}")

    if args.update_intellij:
        home_directory = os.getenv("HOME")
        input_path = get_input_path(args.input, args.intellij_version, home_directory)

        output_path = get_output_path(input_path, args.output)
        with open(input_path, 'r') as f:
            root = ET.fromstring(f.read())

            for module in modules:
                path_to_module = f"{path_to_connectors}{module}"
                path_to_requirements_file = f"{path_to_module}/requirements.txt"
                requirements_file_exists = os.path.exists(path_to_requirements_file)
                print(f"Adding {module} to jdk table")
                add_venv_to_xml_root(module, path_to_module, root)
            with open(output_path, "w") as fout:
                fout.write(ET.tostring(root, encoding="unicode"))
    print("Done.")


# --- tests ---
def setup_module():
    global pytest
    global mock


if "pytest" in sys.argv[0]:
    import unittest


    class TestNoneTypeError(unittest.TestCase):
        def test_output_is_input_if_not_set(self):
            input_path = "/input_path"
            output_path = get_output_path(input_path, None)
            assert input_path == output_path

        def test_get_output_path(self):
            input_path = "/input_path"
            output_path = "/input_path"
            assert output_path == get_output_path(input_path, output_path)

        @unittest.mock.patch("os.walk")
        def test_input_is_selected(self, mock_os):
            os.walk.return_value = iter(
                (("./test1", ["consentOptions", "IdeaIC2021.3", "PyCharmCE2021.3"], []),))
            os.getenv.return_value = "{HOME}"
            input_from_args = None
            version = "IdeaIC2021.3"
            input_path = get_input_path(input_from_args, version, "{HOME}")
            assert "{HOME}/Library/Application Support/JetBrains/IdeaIC2021.3/options/jdk.table.xml" == input_path

        @unittest.mock.patch("os.walk")
        def test_input_single_intellij_version(self, mock_os):
            os.walk.return_value = iter(
                (("./test1", ["consentOptions", "IdeaIC2021.3"], []),))
            input_from_args = None

            version = None
            input_path = get_input_path(input_from_args, version, "{HOME}")
            assert "{HOME}/Library/Application Support/JetBrains/IdeaIC2021.3/options/jdk.table.xml" == input_path

        @unittest.mock.patch("os.walk")
        def test_input_multiple_intellij_versions(self, mock_os):
            os.walk.return_value = iter(
                (('./test1', ['consentOptions', 'IdeaIC2021.3', "PyCharmCE2021.3"], []),))
            input_from_args = None

            version = None
            self.assertRaises(RuntimeError, get_input_path, input_from_args, version, "{HOME}")
