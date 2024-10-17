# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Script to upload and run the cloud benchmark test.

Uses PyAirbyte to rotate AWS credentials for integration tests.

Usage:
    cd scripts
    poetry run python rotate_creds.py

Inline dependency metadata for `uv`:

# /// script
# requires-python = "==3.10"
# dependencies = [
#     "airbyte",  # PyAirbyte
# ]
# ///
"""

from __future__ import annotations

from contextlib import suppress
from subprocess import check_output

import orjson
from anyio import Path

import airbyte as ab
from airbyte.cloud.experimental import CloudConnection, CloudWorkspace, SyncResult
from airbyte.destinations import get_noop_destination


CONNECTOR_NAME = "source-s3"
LOCAL_EXECUTABLE = check_output(f"poetry run which {CONNECTOR_NAME}")


def create_source_obj() -> ab.Source:
    return ab.get_source(
        "source-s3",
        local_executable=LOCAL_EXECUTABLE,
        config=orjson.loads(Path("secrets/config.json").read_text()),
        streams="*",
        install_if_missing=False,
    )


def main() -> None:
    source_id: str | None = None
    destination_id: str | None = None
    connection: CloudConnection | None = None
    workspace = CloudWorkspace(
        workspace_id=ab.get_secret("AIRBYTE_CLOUD_WORKSPACE_ID"),
        api_key=ab.get_secret("AIRBYTE_CLOUD_API_KEY"),
    )
    try:
        source_id = workspace.deploy_source(create_source_obj())
        print(f"Successfully deployed source ID: {source_id}")

        destination_id = workspace.deploy_destination(get_noop_destination())
        print(f"Successfully deployed destination ID: {destination_id}")

        connection = workspace.deploy_connection(
            source=source_id,
            destination=destination_id,
        )
        print(f"Successfully deployed connection ID: {connection.id}")

        print("Running sync...")
        sync_result: SyncResult = connection.run_sync(wait=True)
        print(
            f"""
            Job Status: {sync_result.get_job_status()}
            Job ID: {sync_result.job_id}
            Job URL: {sync_result.job_url}
            Start Time: {sync_result.start_time}
            Records Synced: {sync_result.records_synced}
            Bytes Synced: {sync_result.bytes_synced}
            List of Stream Names: {', '.join(sync_result.stream_names)}
            """
        )
    finally:
        # Clean up (aka permanently delete) all created resources
        if connection:
            with suppress(Exception):
                connection.permanently_delete(
                    delete_source=True,
                    delete_destination=True,
                )
        else:
            if source_id:
                with suppress(Exception):
                    workspace.permanently_delete_source(source_id)

            if destination_id:
                with suppress(Exception):
                    workspace.permanently_delete_destination(destination_id)


if __name__ == "__main__":
    main()
