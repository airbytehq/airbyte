#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from .cloud_availability_updater import deploy_eligible_connectors
from .enrichments import get_enriched_catalog
from .inputs import CLOUD_CATALOG, OSS_CATALOG
from .validations import get_qa_report, get_connectors_eligible_for_cloud

def main():
    enriched_catalog = get_enriched_catalog(OSS_CATALOG, CLOUD_CATALOG)
    qa_report = get_qa_report(enriched_catalog)
    connectors_eligible_for_cloud = get_connectors_eligible_for_cloud(qa_report)
    deploy_eligible_connectors(connectors_eligible_for_cloud)
    #qa_report.to_json(GCS_QA_REPORT_PATH, orient="records")
