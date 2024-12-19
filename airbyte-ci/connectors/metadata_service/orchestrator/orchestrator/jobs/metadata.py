#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dagster import AssetSelection, define_asset_job


stale_gcs_latest_metadata_file_inclusive = AssetSelection.keys("stale_gcs_latest_metadata_file").upstream()
generate_stale_gcs_latest_metadata_file = define_asset_job(
    name="generate_stale_metadata_report", selection=stale_gcs_latest_metadata_file_inclusive
)
