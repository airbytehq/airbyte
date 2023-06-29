from dagster import build_op_context

from orchestrator.resources.gcp import gcp_gcs_client, gcs_directory_blobs, gcs_file_manager
from orchestrator.assets.connector_test_report import generate_nightly_report, persist_connectors_test_summary_files
from orchestrator.config import NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME, NIGHTLY_FOLDER, NIGHTLY_COMPLETE_REPORT_FILE_NAME, REPORT_FOLDER


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
            {"gcs_bucket": {"env": "CI_REPORT_BUCKET"}, "prefix": NIGHTLY_FOLDER, "match_regex": f".*{NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME}$"}
        ),
    }

    context = build_op_context(resources=resources)
    generate_nightly_report(context).value


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
