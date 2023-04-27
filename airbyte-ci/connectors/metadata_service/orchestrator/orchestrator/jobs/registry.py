from dagster import define_asset_job, AssetSelection

registries_inclusive = AssetSelection.keys(
    "metadata_directory_report", "cloud_registry_from_metadata", "oss_registry_from_metadata", "specs_secrets_mask_yaml"
).upstream()
generate_registry = define_asset_job(name="generate_registry", selection=registries_inclusive)

registry_reports_inclusive = AssetSelection.keys("connector_registry_report").upstream()
generate_registry_reports = define_asset_job(name="generate_registry_reports", selection=registry_reports_inclusive)

metadata_inclusive = AssetSelection.keys("persist_metadata_definitions").upstream()
generate_local_metadata_files = define_asset_job(name="generate_local_metadata_files", selection=metadata_inclusive)
