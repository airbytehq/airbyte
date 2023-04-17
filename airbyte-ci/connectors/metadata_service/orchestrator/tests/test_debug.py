from dagster import build_op_context

from orchestrator.resources.gcp import gcp_gcs_client, gcs_bucket_manager, gcs_file_manager, gcs_file_blob
from orchestrator.resources.github import github_client, github_connector_repo, github_connectors_directory

from orchestrator.assets.catalog import (
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
    latest_oss_catalog_dict,
    latest_cloud_catalog_dict,
)
from orchestrator.assets.metadata import (
    catalog_derived_metadata_definitions,
)


from orchestrator.config import REPORT_FOLDER, CATALOG_FOLDER, CONNECTORS_PATH, CONNECTOR_REPO_NAME


def debug_catalog_projection():
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
            {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REPORT_FOLDER}
        ),
        "latest_oss_catalog_gcs_file": gcs_file_blob.configured({"prefix": CATALOG_FOLDER, "gcs_filename": "oss_catalog.json"}),
        "latest_cloud_catalog_gcs_file": gcs_file_blob.configured({"prefix": CATALOG_FOLDER, "gcs_filename": "cloud_catalog.json"}),
    }

    context = build_op_context(resources=resources)
    cloud_catalog_dict = latest_cloud_catalog_dict(context)
    cloud_destinations_df = cloud_destinations_dataframe(cloud_catalog_dict).value
    cloud_sources_df = cloud_sources_dataframe(cloud_catalog_dict).value

    oss_catalog_dict = latest_oss_catalog_dict(context)
    oss_destinations_df = oss_destinations_dataframe(oss_catalog_dict).value
    oss_sources_df = oss_sources_dataframe(oss_catalog_dict).value
    # github_connector_folders_list = github_connector_folders(context).value

    catalog_derived_metadata_definitions(context, cloud_sources_df, cloud_destinations_df, oss_sources_df, oss_destinations_df).value
    # valid_metadata_report_dataframe_df = valid_metadata_report_dataframe(metadata_definitions_df).value

    # all_sources_df = all_sources_dataframe(cloud_sources_df, oss_sources_df, github_connector_folders_list, valid_metadata_report_dataframe_df)
    # all_destinations_df = all_destinations_dataframe(cloud_destinations_df, oss_destinations_df)

    # connector_catalog_location_html(context, all_sources_df, all_destinations_df)
    # connector_catalog_location_markdown(context, all_sources_df, all_destinations_df)
