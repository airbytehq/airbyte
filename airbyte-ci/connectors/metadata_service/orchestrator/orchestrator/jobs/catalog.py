#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from dagster import define_asset_job

generate_catalog = define_asset_job(name="generate_catalog", selection=["metadata_directory_report", "metadata_definitions"])
generate_catalog_markdown = define_asset_job(
    name="generate_catalog_markdown", selection=["connector_catalog_location_html", "connector_catalog_location_markdown"]
)
generate_local_metadata_files = define_asset_job(name="generate_local_metadata_files", selection=["persist_metadata_definitions"])
generate_specs_secrets_mask_file = define_asset_job(name="generate_specs_secrets_mask_file", selection=["persist_specs_secrets_mask"])
