#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pandas as pd
from .models import QAReport

GCS_QA_REPORT_PATH = "gs://prod-airbyte-cloud-connector-metadata-service/qa_report.json"
DUMMY_REPORT = pd.DataFrame([
        {
            "connector_type": "source",
            "connector_name": "test",
            "docker_image_tag": "0.0.0",
            "release_stage": "alpha",
            "is_on_cloud": False,
            "latest_build_is_successful": False,
            "documentation_is_available": False,
            "number_of_connections": 0,
            "number_of_users": 0,
            "sync_success_rate": .99
        }
    ])

def write_qa_report_to_gcs(qa_report: pd.DataFrame, output_file_path: str):
    # Validate the report structure with pydantic QAReport model.
    QAReport(connectors_qa_report=qa_report.to_dict(orient="records"))
    qa_report.to_json(output_file_path, orient="records")

def main():
    write_qa_report_to_gcs(DUMMY_REPORT, GCS_QA_REPORT_PATH)
