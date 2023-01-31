#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

"""
All invocations of this script must be run from the Airbyte repository root.

To Run tests:
pytest ./tools/bin/build_report.py

To run the script:
pip install slack-sdk pyyaml
python ./tools/bin/build_report.py
"""

import os
import pathlib
import re
import sys
from typing import Dict, List, Optional

import requests
import yaml
from slack_sdk import WebhookClient
from slack_sdk.errors import SlackApiError

# Global statics
CONNECTOR_DEFINITIONS_DIR = "./airbyte-config/init/src/main/resources/seed"
SOURCE_DEFINITIONS_YAML = f"{CONNECTOR_DEFINITIONS_DIR}/source_definitions.yaml"
DESTINATION_DEFINITIONS_YAML = f"{CONNECTOR_DEFINITIONS_DIR}/destination_definitions.yaml"
CONNECTORS_ROOT_PATH = "./airbyte-integrations/connectors"
RELEVANT_BASE_MODULES = ["base-normalization", "source-acceptance-test"]
CONNECTOR_BUILD_OUTPUT_URL = "https://dnsgjos7lj2fu.cloudfront.net/tests/summary/connectors"

# Global vars
TESTED_SOURCE = []
TESTED_DESTINATION = []
SUCCESS_SOURCE = []
SUCCESS_DESTINATION = []
NO_TESTS = []
FAILED_LAST = []
FAILED_2_LAST = []


def get_status_page(connector) -> str:
    response = requests.get(f"{CONNECTOR_BUILD_OUTPUT_URL}/{connector}/index.html")
    if response.status_code == 200:
        return response.text


def parse(page) -> list:
    history = []
    for row in re.findall(r"<tr>(.*?)</tr>", page):
        cols = re.findall(r"<td>(.*?)</td>", row)
        if not cols or len(cols) != 3:
            continue
        history.append(
            {
                "date": cols[0],
                "status": re.findall(r" (\S+)</span>", cols[1])[0],
                "link": re.findall(r'href="(.*?)"', cols[2])[0],
            }
        )
    return history


def check_module(connector):
    status_page = get_status_page(connector)

    # check if connector is tested
    if not status_page:
        NO_TESTS.append(connector)
        print("F", end="", flush=True)
        return

    print(".", end="", flush=True)

    if connector.startswith("source"):
        TESTED_SOURCE.append(connector)
    elif connector.startswith("destination"):
        TESTED_DESTINATION.append(connector)

    # order: recent values goes first
    history = parse(status_page)
    # order: recent values goes last
    short_status = "".join(["✅" if build["status"] == "success" else "❌" for build in history[::-1]])  # ex: ❌✅✅❌✅✅❌❌

    # check latest build status
    last_build = history[0]
    if last_build["status"] == "success":
        if connector.startswith("source"):
            SUCCESS_SOURCE.append(connector)
        elif connector.startswith("destination"):
            SUCCESS_DESTINATION.append(connector)
    else:
        failed_today = [connector, short_status, last_build["link"], last_build["date"]]

        if len(history) > 1 and history[1]["status"] != "success":
            FAILED_2_LAST.append(failed_today)
            return

        FAILED_LAST.append(failed_today)


def failed_report(failed_report) -> str:
    max_name_len = max([len(connector[0]) for connector in failed_report])
    max_status_len = max(len(connector[1]) for connector in failed_report)
    for connector in failed_report:
        connector[0] = connector[0].ljust(max_name_len, " ")
        connector[1] = connector[1].rjust(max_status_len, " ")
    return "\n".join([" ".join(connector) for connector in failed_report])


def create_report(connectors, statuses: List[str]) -> str:
    sources_len = len([name for name in connectors if name.startswith("source")])
    destinations_len = len([name for name in connectors if name.startswith("destination")])

    report = f"""
CONNECTORS:   total: {len(connectors)} {" & ".join(statuses)} connectors
Sources:      total: {sources_len} / tested: {len(TESTED_SOURCE)} / success: {len(SUCCESS_SOURCE)} ({round(len(SUCCESS_SOURCE) / sources_len * 100, 1)}%)
Destinations: total: {destinations_len} / tested: {len(TESTED_DESTINATION)} / success: {len(SUCCESS_DESTINATION)} ({round(len(SUCCESS_DESTINATION) / destinations_len * 100, 1)}%)

"""
    if FAILED_LAST:
        report += f"FAILED LAST BUILD ONLY - {len(FAILED_LAST)} connectors:\n" + failed_report(FAILED_LAST) + "\n\n"

    if FAILED_2_LAST:
        report += f"FAILED TWO LAST BUILDS - {len(FAILED_2_LAST)} connectors:\n" + failed_report(FAILED_2_LAST) + "\n\n"

    if NO_TESTS:
        report += f"NO TESTS - {len(NO_TESTS)} connectors:\n" + "\n".join(NO_TESTS) + "\n"

    return report


def send_report(report):
    webhook = WebhookClient(os.environ["SLACK_BUILD_REPORT"])
    try:

        def chunk_messages(report):
            """split report into messages with no more than 4000 chars each (slack limitation)"""
            msg = ""
            for line in report.splitlines():
                msg += line + "\n"
                if len(msg) > 3500:
                    yield msg
                    msg = ""
            yield msg

        for msg in chunk_messages(report):
            webhook.send(text=f"```{msg}```")
        print("Report has been sent")
    except SlackApiError as e:
        print("Unable to send report")
        assert e.response["error"]


def parse_dockerfile_repository_label(dockerfile_contents: str) -> Optional[str]:
    parsed_label = re.findall(r"LABEL io.airbyte.name=(.*)[\s\n]*", dockerfile_contents)
    if len(parsed_label) == 1:
        return parsed_label[0]
    elif len(parsed_label) == 0:
        return None
    else:
        raise Exception(f"found more than one label in dockerfile: {dockerfile_contents}")


def get_docker_label_to_connector_directory(base_directory: str, connector_module_names: List[str]) -> Dict[str, str]:
    result = {}
    for connector in connector_module_names:
        # parse the dockerfile label if the dockerfile exists
        dockerfile_path = pathlib.Path(base_directory, connector, "Dockerfile")
        if os.path.isfile(dockerfile_path):
            print(f"Reading {dockerfile_path}")
            with open(dockerfile_path, "r") as file:
                dockerfile_contents = file.read()
                label = parse_dockerfile_repository_label(dockerfile_contents)
                if label:
                    result[label] = connector
                else:
                    print(f"Couldn't find a connector label in {dockerfile_path}")
        else:
            print(f"Couldn't find a dockerfile at {dockerfile_path}")
    return result


def get_connectors_with_release_stage(definitions_yaml: List, stages: List[str]) -> List[str]:
    """returns e.g: ['airbyte/source-salesforce', ...] when given 'generally_available' as input"""
    return [definition["dockerRepository"] for definition in definitions_yaml if definition.get("releaseStage", "alpha") in stages]


def read_definitions_yaml(path: str):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def get_connectors_with_release_stages(base_directory: str, connectors: List[str], relevant_stages=["beta", "generally_available"]):
    # TODO currently this also excludes shared libs like source-jdbc, we probably shouldn't do that, so we can get the build status of those
    #  modules as well.
    connector_label_to_connector_directory = get_docker_label_to_connector_directory(base_directory, connectors)

    connectors_with_desired_status = get_connectors_with_release_stage(
        read_definitions_yaml(SOURCE_DEFINITIONS_YAML), relevant_stages
    ) + get_connectors_with_release_stage(read_definitions_yaml(DESTINATION_DEFINITIONS_YAML), relevant_stages)
    # return appropriate directory names
    return [
        connector_label_to_connector_directory[label]
        for label in connectors_with_desired_status
        if label in connector_label_to_connector_directory
    ]


def setup_module():
    global pytest
    global mock


if __name__ == "__main__":

    # find all connectors and filter to beta and GA
    connectors = sorted(os.listdir(CONNECTORS_ROOT_PATH))
    relevant_stages = ["beta", "generally_available"]
    relevant_connectors = get_connectors_with_release_stages(CONNECTORS_ROOT_PATH, connectors, relevant_stages)
    print(f"Checking {len(relevant_connectors)} relevant connectors out of {len(connectors)} total connectors")

    # analyse build results for each connector
    [check_module(connector) for connector in relevant_connectors]
    [check_module(base) for base in RELEVANT_BASE_MODULES]

    report = create_report(relevant_connectors, relevant_stages)
    print(report)
    send_report(report)
    print("Finish")
elif "pytest" in sys.argv[0]:
    import unittest

    class Tests(unittest.TestCase):
        def test_filter_definitions_yaml(self):
            mock_def_yaml = [
                {"releaseStage": "alpha", "dockerRepository": "alpha_connector"},
                {"releaseStage": "beta", "dockerRepository": "beta_connector"},
                {"releaseStage": "generally_available", "dockerRepository": "GA_connector"},
            ]
            assert ["alpha_connector"] == get_connectors_with_release_stage(mock_def_yaml, ["alpha"])
            assert ["alpha_connector", "beta_connector"] == get_connectors_with_release_stage(mock_def_yaml, ["alpha", "beta"])
            assert ["beta_connector", "GA_connector"] == get_connectors_with_release_stage(mock_def_yaml, ["beta", "generally_available"])
            assert ["GA_connector"] == get_connectors_with_release_stage(mock_def_yaml, ["generally_available"])

        def test_parse_dockerfile_label(self):
            mock_dockerfile = """
ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]

LABEL io.airbyte.version=1.0.8
LABEL io.airbyte.name=airbyte/source-salesforce"""
            assert "airbyte/source-salesforce" == parse_dockerfile_repository_label(mock_dockerfile)
