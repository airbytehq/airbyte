from dagster import define_asset_job


generate_catalog_markdown = define_asset_job(name="generate_catalog_markdown", selection="*")
