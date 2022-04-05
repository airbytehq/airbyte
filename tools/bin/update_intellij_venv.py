import argparse
import os
import xml.etree.ElementTree as ET

INTELLIJ_VERSION_FLAG = "-version"


def add_venv_to_xml_root(module: str, module_full_path: str, python_version: str, xml_root):
    table = xml_root.find("component")
    jdk_node = ET.SubElement(table, 'jdk', {"version": "2"})
    ET.SubElement(jdk_node, "name", {"value": f"{python_version} ({module})"})
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
                                              f'file://{module_full_path}/.venv/lib/{python_version}/site-packages',
                                          "type": "simple"
                                          })


def create_parser():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-python", required=True, help="Python version")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-modules', nargs='?', help='Modules to add')
    group.add_argument('--all-modules', action='store_true')

    parser.add_argument("-input", help="Path to input jdk table")
    parser.add_argument("-intellij-version", help="Intellij version to use")
    parser.add_argument("-output", help="Path to output jdk table")
    parser.add_argument(INTELLIJ_VERSION_FLAG, help="Instance of IntelliJ to update")

    parser.add_argument('-airbyte', default=f"{os.path.dirname(__file__)}/../..", help='Path to Airbyte root directory')
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    path_to_connectors = f"{args.airbyte}/airbyte-integrations/connectors/"

    input_path = args.input
    if input_path is None:
        home_directory = os.getenv('HOME')
        path_to_intellij_settings = f"{home_directory}/Library/Application Support/JetBrains/"
        intellij_versions = next(os.walk(path_to_intellij_settings))[1]
        intellij_versions = [iv for iv in intellij_versions if iv != "consentOptions"]
        if args.version in intellij_versions:
            intellij_instance_to_update = args.version
        elif len(intellij_versions) == 1:
            intellij_instance_to_update = intellij_versions[1]
            print(intellij_instance_to_update)
        else:
            print(
                f"Please select which instance of Intellij to update with the `{INTELLIJ_VERSION_FLAG}` flag. Options are: {intellij_versions}")
            sys.exit(-1)
        input_path = f"{path_to_intellij_settings}/{intellij_instance_to_update}/options/jdk.table.xml"

    output_path = args.output
    if output_path is None:
        output_path = input_path

    if args.all_modules:
        print(path_to_connectors)
        modules = next(os.walk(path_to_connectors))[1]
    else:
        modules = args.modules.split(",")
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
        with open(output_path, 'w') as fout:
            fout.write(ET.tostring(root, encoding="unicode"))
