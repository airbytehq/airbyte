#!/usr/bin/env python3
#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

# pip3 install docker
# pip3 install PyYAML


import json
import logging
import os
import re
import subprocess

import docker
import yaml

SOURCE_DEFINITIONS = "airbyte-config/init/src/main/resources/seed/source_definitions.yaml"
DESTINATION_DEFINITIONS = "airbyte-config/init/src/main/resources/seed/destination_definitions.yaml"
SPECS_DIR = "specs"
SPEC_FILE = "spec.json"
PATTERNS = [
    "token",
    "secret",
    "password",
    "key",
    "client_id",
    "service_account",
    "tenant_id",
    "certificate",
    "jwt",
    "credentials",
    "app_id",
    "appid",
]


def git_toplevel():
    process = subprocess.run(
        ["git", "-C", os.path.dirname(__file__), "rev-parse", "--show-toplevel"], check=True, capture_output=True, universal_newlines=True
    )
    return process.stdout.strip()


def get_connectors(filename):
    toplevel = git_toplevel()
    with open(os.path.join(toplevel, filename)) as fp:
        definitions = yaml.safe_load(fp)
    res = {}
    for item in definitions:
        connector_name = item["dockerRepository"][len("airbyte/") :]
        docker_image = item["dockerRepository"] + ":" + item["dockerImageTag"]
        res[connector_name] = docker_image
    return res


def docker_run(client, docker_image):
    try:
        res = client.containers.run(image=docker_image, command=["spec"], detach=False, remove=True)
        return res.decode("utf-8")
    except docker.errors.ContainerError as e:
        logging.exception(e)


def get_spec(output):
    for line in output.splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        else:
            if obj.get("type") == "SPEC":
                return obj


def generate_all_specs():
    client = docker.from_env()
    connectors = get_connectors(SOURCE_DEFINITIONS) | get_connectors(DESTINATION_DEFINITIONS)
    for connector_name, docker_image in connectors.items():
        logging.info(f"docker run -ti --rm {docker_image} spec")
        output = docker_run(client, docker_image)
        if output:
            spec = get_spec(output)
            if spec:
                dirname = os.path.join(SPECS_DIR, connector_name)
                os.makedirs(dirname, exist_ok=True)
                with open(os.path.join(dirname, SPEC_FILE), "w") as fp:
                    fp.write(json.dumps(spec, indent=2))


def iter_all_specs(dirname):
    for root, dirs, files in os.walk(dirname):
        if SPEC_FILE in files:
            filename = os.path.join(root, SPEC_FILE)
            with open(filename) as fp:
                try:
                    obj = json.load(fp)
                except ValueError:
                    continue
                if obj.get("type") == "SPEC":
                    yield filename, obj


def find_properties(properties, path=None):
    "find all properties recursively"
    if path is None:
        path = []

    for prop_name, prop_obj in properties.items():
        if isinstance(prop_obj, dict):
            if prop_obj.get("type") == "object":
                if "properties" in prop_obj:
                    yield from find_properties(prop_obj["properties"], path=path + [prop_name])
                elif "oneOf" in prop_obj:
                    for n, oneof in enumerate(prop_obj["oneOf"]):
                        yield from find_properties(oneof["properties"], path=path + [prop_name, f"[{n}]"])
            elif prop_obj.get("type", "string") == "array" and prop_obj["items"].get("type") == "object":
                yield from find_properties(prop_obj["items"]["properties"], path=path + [prop_name])
            else:
                yield path, prop_name, prop_obj


def main():
    if not os.path.exists(SPECS_DIR):
        generate_all_specs()

    PATTERN = re.compile("|".join(PATTERNS), re.I)

    for filename, obj in iter_all_specs(SPECS_DIR):
        spec = obj["spec"]
        for prop_path, prop_name, prop_obj in find_properties(spec):
            if prop_obj.get("type") != "boolean" and not prop_obj.get("airbyte_secret") and PATTERN.search(prop_name):
                print(filename, ".".join(prop_path + [prop_name]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
