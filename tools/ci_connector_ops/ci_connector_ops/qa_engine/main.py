#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from . import cloud_availability_updater, enrichments, inputs, validations
from .constants import CLOUD_CATALOG_URL, OSS_CATALOG_URL

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def main():
    logger.info("Fetch the OSS connectors catalog.")
    oss_catalog = inputs.fetch_remote_catalog(OSS_CATALOG_URL)
    logger.info("Fetch the Cloud connectors catalog.")
    cloud_catalog = inputs.fetch_remote_catalog(CLOUD_CATALOG_URL)
    logger.info("Fetch adoption metrics.")
    adoption_metrics_per_connector_version = inputs.fetch_adoption_metrics_per_connector_version()
    logger.info("Start the enriched catalog generation.")
    enriched_catalog = enrichments.get_enriched_catalog(oss_catalog, cloud_catalog, adoption_metrics_per_connector_version)
    logger.info("Start the QA report generation.")
    qa_report = validations.get_qa_report(enriched_catalog, len(oss_catalog))
    logger.info("Start the QA report generation.")
    eligible_connectors = validations.get_connectors_eligible_for_cloud(qa_report)
    logger.info("Start eligible connectors deployment to Cloud.")
    cloud_availability_updater.deploy_eligible_connectors_to_cloud_repo(eligible_connectors)
