#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import dagster
import pandas as pd
from dagster import build_op_context
from dagster_slack import SlackResource
from metadata_service.constants import METADATA_FILE_NAME, METADATA_FOLDER
from orchestrator import GITHUB_RESOURCE_TREE, METADATA_RESOURCE_TREE, REGISTRY_ENTRY_RESOURCE_TREE
from orchestrator.assets.connector_test_report import generate_nightly_report, persist_connectors_test_summary_files
from orchestrator.assets.github import github_metadata_file_md5s, stale_gcs_latest_metadata_file
from orchestrator.assets.registry import persisted_oss_registry
from orchestrator.assets.registry_entry import metadata_entry, registry_entry
from orchestrator.config import NIGHTLY_COMPLETE_REPORT_FILE_NAME, NIGHTLY_FOLDER, NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME, REPORT_FOLDER
from orchestrator.resources.gcp import gcp_gcs_client, gcs_directory_blobs, gcs_file_manager


def debug_nightly_report():
    resources = {
        "gcp_gcs_client": gcp_gcs_client.configured(
            {
                "gcp_gcs_cred_string": {"env": "GCS_CREDENTIALS"},
            }
        ),
        "latest_nightly_complete_file_blobs": gcs_directory_blobs.configured(
            {"gcs_bucket": {"env": "CI_REPORT_BUCKET"}, "prefix": NIGHTLY_FOLDER, "match_regex": f".*{NIGHTLY_COMPLETE_REPORT_FILE_NAME}$"}
        ),
        "latest_nightly_test_output_file_blobs": gcs_directory_blobs.configured(
            {
                "gcs_bucket": {"env": "CI_REPORT_BUCKET"},
                "prefix": NIGHTLY_FOLDER,
                "match_regex": f".*{NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME}$",
            }
        ),
    }

    context = build_op_context(resources=resources)
    generate_nightly_report(context).value


def debug_registry():
    context = build_op_context(resources=REGISTRY_ENTRY_RESOURCE_TREE)
    persisted_oss_registry(context).value


def debug_github_folders():
    context = build_op_context(
        resources={
            **GITHUB_RESOURCE_TREE,
            **METADATA_RESOURCE_TREE,
        }
    )
    github_md5s = github_metadata_file_md5s(context).value
    stale_gcs_latest_metadata_file(context, github_md5s).value


def debug_badges():
    resources = {
        "gcp_gcs_client": gcp_gcs_client.configured(
            {
                "gcp_gcs_cred_string": {"env": "GCS_CREDENTIALS"},
            }
        ),
        "registry_report_directory_manager": gcs_file_manager.configured(
            {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": REPORT_FOLDER}
        ),
    }

    context = build_op_context(resources=resources)
    persist_connectors_test_summary_files(context).value


def debug_registry_entry():

    resources = {
        "gcp_gcs_client": gcp_gcs_client.configured(
            {
                "gcp_gcs_cred_string": {"env": "GCS_CREDENTIALS"},
            }
        ),
        "all_metadata_file_blobs": gcs_directory_blobs.configured(
            {"gcs_bucket": {"env": "METADATA_BUCKET"}, "prefix": METADATA_FOLDER, "match_regex": f".*latest/{METADATA_FILE_NAME}$"}
        ),
        "slack": SlackResource(token="DUMMY"),
    }

    part_key = "CNaH/OOd74UDEAE="
    empty_dataframe = pd.DataFrame()

    context = build_op_context(resources=resources, partition_key=part_key)
    metadata_entry_val = metadata_entry(context, empty_dataframe)
