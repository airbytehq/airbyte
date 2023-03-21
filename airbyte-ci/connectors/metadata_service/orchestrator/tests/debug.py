from dagster import build_op_context

from orchestrator.resources.gcp_resources import gcp_gcs_client, gcs_bucket_manager, gcs_file_manager, gcs_file_blob
from orchestrator.resources.github_resources import github_client, github_connector_repo, github_connectors_directory
from orchestrator.assets.catalog_assets import (
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
    latest_oss_catalog_dict,
    latest_cloud_catalog_dict,
    all_sources_dataframe,
    all_destinations_dataframe,
    connector_catalog_location_markdown,
    connector_catalog_location_html,
    metadata_definitions,
    valid_metadata_list,
)
from orchestrator.assets.github_assets import source_controlled_connectors

from orchestrator.config import REPORT_FOLDER, CATALOG_FOLDER, CONNECTORS_PATH, CONNECTOR_REPO_NAME


def test_debug_catalog_projection():
    """
    This is a debug function that is used to test the catalog projection end to end.

    This is currently the only way to be able to set breakpoints in the catalog projection code.

    It is not intended to be used in production.
    """

    resources = {
        "github_client": github_client,
        "github_connector_repo": github_connector_repo.configured({"connector_repo_name": CONNECTOR_REPO_NAME}),
        "github_connectors_directory": github_connectors_directory.configured({"connectors_path": CONNECTORS_PATH}),
        "gcp_gcs_client": gcp_gcs_client.configured(
            {
                "gcp_gcs_cred_string": {"env": "GCS_CREDENTIALS"},
            }
        ),
        "gcs_bucket_manager": gcs_bucket_manager.configured({"gcs_bucket": {"env": "METADATA_BUCKET"}}),
        "catalog_report_directory_manager": gcs_file_manager.configured(
            {"gcs_bucket": {"env": "METADATA_BUCKET"}, "gcs_prefix": REPORT_FOLDER}
        ),
        "latest_oss_catalog_gcs_file": gcs_file_blob.configured({"gcs_prefix": CATALOG_FOLDER, "gcs_filename": "oss_catalog.json"}),
        "latest_cloud_catalog_gcs_file": gcs_file_blob.configured({"gcs_prefix": CATALOG_FOLDER, "gcs_filename": "cloud_catalog.json"}),
    }

    context = build_op_context(resources=resources)
    cloud_catalog_dict = latest_cloud_catalog_dict(context)
    cloud_destinations_df = cloud_destinations_dataframe(cloud_catalog_dict)
    cloud_sources_df = cloud_sources_dataframe(cloud_catalog_dict)

    oss_catalog_dict = latest_oss_catalog_dict(context)
    oss_destinations_df = oss_destinations_dataframe(oss_catalog_dict)
    oss_sources_df = oss_sources_dataframe(oss_catalog_dict)
    source_controlled_connectors_df = source_controlled_connectors(context)

    metadata_definitions_df = metadata_definitions(cloud_sources_df, cloud_destinations_df, oss_sources_df, oss_destinations_df)
    valid_metadata_list_df = valid_metadata_list(metadata_definitions_df)

    all_sources_df = all_sources_dataframe(cloud_sources_df, oss_sources_df, source_controlled_connectors_df, valid_metadata_list_df)
    # all_destinations_df = all_destinations_dataframe(cloud_destinations_df, oss_destinations_df)

    # connector_catalog_location_html(context, all_sources_df, all_destinations_df)
    # connector_catalog_location_markdown(context, all_sources_df, all_destinations_df)
