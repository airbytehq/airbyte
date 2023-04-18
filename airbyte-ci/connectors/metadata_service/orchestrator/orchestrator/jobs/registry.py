from dagster import define_asset_job, AssetSelection

metadata_definitions_inclusive = AssetSelection.keys("metadata_directory_report", "metadata_definitions").upstream()
registry_reports_inclusive = AssetSelection.keys("connector_registry_location_html", "connector_registry_location_markdown").upstream()

generate_registry = define_asset_job(name="generate_registry", selection=metadata_definitions_inclusive)
generate_registry_markdown = define_asset_job(name="generate_registry_markdown", selection=registry_reports_inclusive)

# TODO Change to a Asset selection
generate_local_metadata_files = define_asset_job(name="generate_local_metadata_files", selection=["persist_metadata_definitions"])
generate_specs_secrets_mask_file = define_asset_job(name="generate_specs_secrets_mask_file", selection=["persist_specs_secrets_mask"])
