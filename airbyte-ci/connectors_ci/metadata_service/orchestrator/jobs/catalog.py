
from dagster import define_asset_job

# ------ Jobs ------ #

generate_catalog_markdown = define_asset_job(name="generate_catalog_markdown", selection="*")

# ------ Sensors ------ #



