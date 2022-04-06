import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

INTELLIJ_VERSION_FLAG = "-version"


def add_venv_to_xml_root(module: str, module_full_path: str, python_version: str, xml_root):
    environment_name = f"{python_version} ({module})"

    table = xml_root.find("component")

    for elem in table:
        for subelem in elem:
            attribute = subelem.attrib
            if attribute.get("value") == environment_name:
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
                                              f"file://{module_full_path}/.venv/lib/{python_version}/site-packages",
                                          "type": "simple"
                                          })


def get_output_path(input_path, output_path):
    if output_path is None:
        return input_path
    else:
        return output_path


def create_parser():
    parser = argparse.ArgumentParser(description="TODO")
    parser.add_argument("-python", required=True, help="Python version")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-modules", nargs="?", help="Modules to add")
    group.add_argument("--all-modules", action="store_true")

    parser.add_argument("-input", help="Path to input jdk table")
    parser.add_argument("-intellij-version", help="Intellij version to use")
    parser.add_argument("-output", help="Path to output jdk table")
    parser.add_argument(INTELLIJ_VERSION_FLAG, help="Instance of IntelliJ to update")
    parser.add_argument("--install-venv", action="store_true", help="TODO")
    parser.add_argument("--update-intellij", action="store_true", help="TODO")

    parser.add_argument("-airbyte", default=f"{os.path.dirname(__file__)}/../..", help="Path to Airbyte root directory")
    return parser


def parse_args(args):
    parser = create_parser()
    return parser.parse_args(args)


def get_input_path(input_from_args, version, home_directory):
    if input_from_args is not None:
        return input_from_args
    else:
        path_to_intellij_settings = f"{home_directory}/Library/Application Support/JetBrains/"
        walk = os.walk(path_to_intellij_settings)
        intellij_versions = [version for version in next(walk)[1] if version != "consentOptions"]
        print(intellij_versions)
        if version in intellij_versions:
            intellij_instance_to_update = version
        elif len(intellij_versions) == 1:
            intellij_instance_to_update = intellij_versions[0]
            print(intellij_instance_to_update)
        else:
            msg = f"Please select which instance of Intellij to update with the `{INTELLIJ_VERSION_FLAG}` flag. Options are: {intellij_versions}"
            print(msg)
            raise RuntimeError(msg)
        return f"{path_to_intellij_settings}{intellij_instance_to_update}/options/jdk.table.xml"


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    path_to_connectors = f"{args.airbyte}/airbyte-integrations/connectors/"

    home_directory = os.getenv("HOME")
    input_path = get_input_path(args.input, args.version, home_directory)

    output_path = get_output_path(input_path, args.output)

    if args.all_modules:
        print(path_to_connectors)
        modules = next(os.walk(path_to_connectors))[1]
    else:
        modules = args.modules.split(",")

    if args.install_venv:
        for module in modules:
            subprocess.run(["tools/bin/setup_connector_venv.sh", module], check=True)
    if args.update_intellij:
        with open(input_path, 'r') as f:
            root = ET.fromstring(f.read())

            for module in modules:
                path_to_module = f"{path_to_connectors}{module}"
                path_to_requirements_file = f"{path_to_module}/requirements.txt"
                requirements_file_exists = os.path.exists(path_to_requirements_file)
                if requirements_file_exists:
                    print(f"Adding {module} to jdk table")
                    add_venv_to_xml_root(module, path_to_module, args.python, root)
                else:
                    print(f"Skipping {module}")
            with open(output_path, "w") as fout:
                fout.write(ET.tostring(root, encoding="unicode"))
    print("Done running")


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
