from dagster import Definitions

from .resources.gcp_resources import gcp_gcs_client, gcp_gcs_metadata_bucket, gcs_file_manager
from .resources.catalog_resources import latest_oss_catalog_gcs_file, latest_cloud_catalog_gcs_file
from .assets.catalog_assets import oss_destinations_dataframe, cloud_destinations_dataframe, oss_sources_dataframe, cloud_sources_dataframe, latest_oss_catalog_dict, latest_cloud_catalog_dict, all_sources_dataframe, all_destinations_dataframe, connector_catalog_location_markdown, connector_catalog_location_html
from .jobs.catalog_jobs import generate_catalog_markdown
from .sensors.catalog_sensors import catalog_updated_sensor

from .config import BUCKET_NAME


assets=[
    oss_destinations_dataframe,
    cloud_destinations_dataframe,
    oss_sources_dataframe,
    cloud_sources_dataframe,
    latest_oss_catalog_dict,
    latest_cloud_catalog_dict,
    all_sources_dataframe,
    all_destinations_dataframe,
    connector_catalog_location_markdown,
    connector_catalog_location_html,
]

resources={
    "gcp_gcs_client": gcp_gcs_client.configured({
        "gcp_gsm_cred_string": {"env": "GCP_GSM_CREDENTIALS"},
    }),
    "gcp_gcs_metadata_bucket": gcp_gcs_metadata_bucket,
    "gcs_test_folder": gcs_file_manager.configured({
        "gcs_bucket": BUCKET_NAME,
        "gcs_prefix": "testy"
    }),
    "latest_oss_catalog_gcs_file": latest_oss_catalog_gcs_file,
    "latest_cloud_catalog_gcs_file": latest_cloud_catalog_gcs_file
}

sensors=[
    catalog_updated_sensor(
        job=generate_catalog_markdown,
        resources_def=resources
    )
]

schedules=[]

jobs=[generate_catalog_markdown]

defn = Definitions(
    jobs=jobs,
    assets=assets,
    resources=resources,
    schedules=schedules,
    sensors=sensors,
)

# def debug_catalog_projection():
#     context = build_op_context(resources={
#         "gcp_gsm_credentials": gcp_gsm_credentials,
#         "gcp_gcs_client": gcp_gcs_client,
#         "gcp_gcs_metadata_bucket": gcp_gcs_metadata_bucket,
#         "latest_oss_catalog_gcs_file": latest_oss_catalog_gcs_file,
#         "latest_cloud_catalog_gcs_file": latest_cloud_catalog_gcs_file
#     })
#     cloud_catalog_dict = latest_cloud_catalog_dict(context)
#     cloud_destinations_df = cloud_destinations_dataframe(cloud_catalog_dict)
#     cloud_sources_df = cloud_sources_dataframe(cloud_catalog_dict)

#     oss_catalog_dict = latest_oss_catalog_dict(context)
#     oss_destinations_df = oss_destinations_dataframe(oss_catalog_dict)
#     oss_sources_df = oss_sources_dataframe(oss_catalog_dict)

#     all_sources_df = all_sources_dataframe(cloud_sources_df, oss_sources_df)
#     all_destinations_df = all_destinations_dataframe(cloud_destinations_df, oss_destinations_df)

#     connector_catalog_location_html(context, all_sources_df, all_destinations_df)

# debug_catalog_projection()
