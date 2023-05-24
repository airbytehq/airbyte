from dagster import define_asset_job, AssetSelection

registries_inclusive = AssetSelection.keys(
    "persist_cloud_registry_from_metadata", "persist_oss_registry_from_metadata", "specs_secrets_mask_yaml"
).upstream()
generate_registry = define_asset_job(name="generate_registry", selection=registries_inclusive)

registry_reports_inclusive = AssetSelection.keys("connector_registry_report").upstream()
generate_registry_reports = define_asset_job(name="generate_registry_reports", selection=registry_reports_inclusive)
