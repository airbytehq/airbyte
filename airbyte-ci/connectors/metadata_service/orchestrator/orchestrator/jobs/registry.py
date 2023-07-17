from dagster import define_asset_job, AssetSelection
from orchestrator.assets import registry_entry

oss_registry_inclusive = AssetSelection.keys("persisted_oss_registry", "specs_secrets_mask_yaml").upstream()
generate_oss_registry = define_asset_job(name="generate_oss_registry", selection=oss_registry_inclusive)

cloud_registry_inclusive = AssetSelection.keys("persisted_cloud_registry", "specs_secrets_mask_yaml").upstream()
generate_cloud_registry = define_asset_job(name="generate_cloud_registry", selection=cloud_registry_inclusive)

registry_reports_inclusive = AssetSelection.keys("connector_registry_report").upstream()
generate_registry_reports = define_asset_job(name="generate_registry_reports", selection=registry_reports_inclusive)

registry_entry_inclusive = AssetSelection.keys("registry_entry").upstream()
generate_registry_entry = define_asset_job(
    name="generate_registry_entry",
    selection=registry_entry_inclusive,
    partitions_def=registry_entry.metadata_partitions_def,
)
