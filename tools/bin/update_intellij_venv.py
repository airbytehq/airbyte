import argparse
import os
import xml.etree.ElementTree as ET


def add_venv_to_xml_root(module: str, xml_root):
    table = xml_root.find("component")
    jdk_node = ET.SubElement(table, 'jdk', {"version": "2"})
    ET.SubElement(jdk_node, "name", {"value": f"Python ({module})"})
    ET.SubElement(jdk_node, "type", {"value": "Python SDK"})
    ET.SubElement(jdk_node, "version", {"value": "Python"})
    ET.SubElement(jdk_node, "homePath",
                  {"value": f"$USER_HOME$/code/airbyte/airbyte-integrations/connectors/{module}/.venv/bin/python"})

    roots = ET.SubElement(jdk_node, "roots")
    annotationsPath = ET.SubElement(roots, "annotationsPath")
    ET.SubElement(annotationsPath, "root", {"type": "composite"})

    classPath = ET.SubElement(roots, "classPath")
    classPathRoot = ET.SubElement(classPath, "root", {"type": "composite"})

    ET.SubElement(classPathRoot, "root", {"url":
                                              f'file://$USER_HOME$/code/airbyte/airbyte-integrations/connectors/{module}/.venv/lib/python3.8/site-packages',
                                          "type": "simple"
                                          })


def create_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-modules', nargs='?', help='Modules to add')
    group.add_argument('--all-modules', nargs='?')

    parser.add_argument("-input", help="Path to input jdk table")
    parser.add_argument("-output", help="Path to output jdk table")

    parser.add_argument('-airbyte', help='Path to Airbyte root directory')
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    path_to_modules = f"{args.airbyte}/airbyte-integrations/connectors/"

    if args.all_modules:
        print(path_to_modules)
        modules = next(os.walk(path_to_modules))[1]
    else:
        modules = args.modules.split(",")
    with open(args.input, 'r') as f:
        root = ET.fromstring(f.read())

        for module in modules:
            path_to_requirements_file = f"{path_to_modules}{module}/requirements.txt"
            requirements_file_exists = os.path.exists(path_to_requirements_file)
            if requirements_file_exists:
                print(f"Adding {module} to jdk table")
                add_venv_to_xml_root(module, root)
            else:
                print(f"Skipping {module}")
        with open(args.output, 'w') as fout:
            fout.write(ET.tostring(root, encoding="unicode"))
