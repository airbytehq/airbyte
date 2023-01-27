#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


CLOUD_CATALOG_URL = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/cloud_catalog.json"
OSS_CATALOG_URL = "https://storage.googleapis.com/prod-airbyte-cloud-connector-metadata-service/oss_catalog.json"

INAPPROPRIATE_FOR_CLOUD_USE_CONNECTORS = [
    "8be1cf83-fde1-477f-a4ad-318d23c9f3c6", # Local CSV
    "a625d593-bba5-4a1c-a53d-2d246268a816", # Local JSON
    "b76be0a6-27dc-4560-95f6-2623da0bd7b6" # Local SQL Lite
]

GCS_QA_REPORT_PATH = "gs://prod-airbyte-cloud-connector-metadata-service/qa_report.json"
