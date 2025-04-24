# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import requests
from bs4 import BeautifulSoup
from google.cloud import storage  # type: ignore

if TYPE_CHECKING:
    from typing import Dict

    from connector_ops.utils import Connector  # type: ignore


TEST_SUMMARY_ROOT_URL = "https://connectors.airbyte.com/files/generated_reports/test_summary"


def get_ci_json_report(json_report_url: str) -> Dict:
    storage_client = storage.Client(project="dataline-integration-testing")
    bucket_name = json_report_url.split("/")[3]
    blob_name = "/".join(json_report_url.split("/")[4:])
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    return json.loads(blob.download_as_string())


def get_ci_on_master_report(connector: Connector) -> Dict | None:
    """This is a hack because we use the HTML report to get the latest CI insights.
    We should ideally fetch the json report directly but the URL has timestamp in it so it's not deterministic.

    Args:
        connector (Connector): The connector to get the CI insights for.

    Returns:
        Dict | None: The CI insights if found, None otherwise.
    """
    url = f"{TEST_SUMMARY_ROOT_URL}/{connector.technical_name}/index.html"

    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, "html.parser")

    rows = soup.find_all("tr")

    for row in rows[1:]:  # Skipping the header row
        columns = row.find_all("td")
        if columns:
            try:
                report_url = columns[3].find("a")["href"]
            except (IndexError, KeyError, TypeError):
                continue
            json_report_url = report_url.replace(".html", ".json")
            # The first table entry is the latest report, but sometimes it's not there questionmark
            try:
                json_report = get_ci_json_report(json_report_url)
                if json_report["connector_version"] == connector.version:
                    return json_report
            except Exception as e:
                continue
            return None

    return None
