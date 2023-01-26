#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from .constants import GCS_QA_REPORT_PATH
from .enrichments import get_enriched_catalog
from .inputs import CLOUD_CATALOG, OSS_CATALOG
from .validations import get_qa_report


def main():
    enriched_catalog = get_enriched_catalog(OSS_CATALOG, CLOUD_CATALOG)
    qa_report = get_qa_report(enriched_catalog)
    qa_report.to_json(GCS_QA_REPORT_PATH, orient="records")
