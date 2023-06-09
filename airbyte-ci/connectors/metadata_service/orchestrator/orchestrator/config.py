from typing import Optional

REGISTRIES_FOLDER = "registries/v0"
REPORT_FOLDER = "generated_reports"

NIGHTLY_FOLDER = "airbyte-ci/connectors/test/nightly_builds/master"
NIGHTLY_COMPLETE_REPORT_FILE_NAME = "complete.json"
NIGHTLY_INDIVIDUAL_TEST_REPORT_FILE_NAME = "output.json"
NIGHTLY_GHA_WORKFLOW_ID = "connector_nightly_builds_dagger.yml"

CONNECTOR_REPO_NAME = "airbytehq/airbyte"
CONNECTORS_PATH = "airbyte-integrations/connectors"
CONNECTORS_TEST_RESULT_BUCKET_URL = "https://dnsgjos7lj2fu.cloudfront.net"


def get_public_url_for_gcs_file(bucket_name: str, file_path: str, cdn_url: Optional[str] = None) -> str:
    """Get the public URL to a file in the GCS bucket.

    Args:
        bucket_name: The name of the GCS bucket.
        file_path: The path to the file in the bucket.
        cdn_url: The base URL of the CDN that serves the bucket.

    Returns:
        The public URL to the file.
    """
    return f"{cdn_url}/{file_path}" if cdn_url else f"https://storage.googleapis.com/{bucket_name}/{file_path}"
