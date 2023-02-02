#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from .constants import CLOUD_CATALOG_URL, OSS_CATALOG_URL
from . import enrichments, inputs, validations


def main():
    oss_catalog = inputs.fetch_remote_catalog(OSS_CATALOG_URL)
    cloud_catalog = inputs.fetch_remote_catalog(CLOUD_CATALOG_URL)
    adoption_metrics_per_connector_version = inputs.fetch_adoption_metrics_per_connector_version()
    enriched_catalog = enrichments.get_enriched_catalog(
        oss_catalog,
        cloud_catalog,
        adoption_metrics_per_connector_version
    )
    validations.get_qa_report(enriched_catalog, len(oss_catalog))
