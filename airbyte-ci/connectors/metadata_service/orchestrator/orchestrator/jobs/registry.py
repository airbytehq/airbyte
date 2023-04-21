from dagster import define_asset_job, AssetSelection

registries_inclusive = AssetSelection.keys(
    "metadata_directory_report", "cloud_registry_from_metadata", "oss_registry_from_metadata"
).upstream()
registry_reports_inclusive = AssetSelection.keys("connector_registry_report").upstream()

generate_registry = define_asset_job(name="generate_registry", selection=registries_inclusive)
generate_registry_reports = define_asset_job(name="generate_registry_reports", selection=registry_reports_inclusive)

# TODO Change to a Asset selection
generate_local_metadata_files = define_asset_job(name="generate_local_metadata_files", selection=["persist_metadata_definitions"])
generate_specs_secrets_mask_file = define_asset_job(name="generate_specs_secrets_mask_file", selection=["persist_specs_secrets_mask"])
