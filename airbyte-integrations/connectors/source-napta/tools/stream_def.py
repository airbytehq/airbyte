# This program reads the content of napta.yaml, which is the swagger definition of an API
# Then it iterates through every API endpoit and stores it in a list

import json
import os

import yaml


def get_endpoints(swagger_file):
    with open(swagger_file, "r") as file:
        swagger_data = yaml.safe_load(file)
        endpoints = []
        seen_paths = set()
        for path, methods in swagger_data["paths"].items():
            for method in methods:
                if method.upper() == "GET":
                    endpoint = {"path": path.split("/")[3], "method": method.upper()}
                    if endpoint["path"] not in seen_paths:
                        seen_paths.add(endpoint["path"])
                        endpoints.append(endpoint)
        return endpoints


def generate_streams_def(endpoints):
    code = ""
    for endpoint in endpoints:
        code += (
            f"class {endpoint['path'].title().replace('_', '')}(NaptaStream):\n"
            + f"    def path(self, **kwargs) -> str:\n"
            + f"        return \"{endpoint['path']}\"\n\n"
        )

    with open("streams_def_gen.py", "w") as file:
        file.write(code)


def generate_streams(endpoints):
    code_export = "["
    code_import = "from .streams import "
    for endpoint in endpoints:
        code_export += f"{endpoint['path'].title().replace('_', '')}(authenticator=authenticator, config=config),\n"
        code_import += f"{endpoint['path'].title().replace('_', '')}, "
    code_export = code_export[:-2] + "]"
    code_import = code_import[:-2]

    with open("streams_gen.py", "w") as file:
        file.write(code_import)
        file.write("\n\n")
        file.write(code_export)


def create_stream_files(endpoints):
    os.makedirs("streams", exist_ok=True)
    for endpoint in endpoints:
        path = endpoint["path"].lstrip("/")
        filename = f"{path}.json"
        filepath = os.path.join("streams", filename)
        with open(filepath, "w") as file:
            json.dump({}, file)


endpoints = get_endpoints("napta.yaml")

generate_streams_def(endpoints)
generate_streams(endpoints)
create_stream_files(endpoints)
