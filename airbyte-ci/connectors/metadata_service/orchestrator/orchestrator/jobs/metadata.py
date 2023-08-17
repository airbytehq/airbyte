from dagster import define_asset_job, AssetSelection

stale_gcs_latest_metadata_file_inclusive = AssetSelection.keys("stale_gcs_latest_metadata_file").upstream()
generate_stale_gcs_latest_metadata_file = define_asset_job(
    name="generate_stale_metadata_report", selection=stale_gcs_latest_metadata_file_inclusive
)
