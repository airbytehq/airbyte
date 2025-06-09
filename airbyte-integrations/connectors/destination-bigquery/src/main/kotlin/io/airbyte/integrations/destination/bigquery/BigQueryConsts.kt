/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

object BigQueryConsts {
    const val MiB: Int = 1024 * 1024
    const val CONFIG_DATASET_ID: String = "dataset_id"
    const val CONFIG_PROJECT_ID: String = "project_id"
    const val CONFIG_DATASET_LOCATION: String = "dataset_location"
    const val CONFIG_CREDS: String = "credentials_json"
    const val BIG_QUERY_CLIENT_CHUNK_SIZE: String = "big_query_client_buffer_size_mb"

    const val LOADING_METHOD: String = "loading_method"
    const val METHOD: String = "method"
    const val GCS_STAGING: String = "GCS Staging"
    const val GCS_BUCKET_NAME: String = "gcs_bucket_name"
    const val GCS_BUCKET_PATH: String = "gcs_bucket_path"
    const val GCS_BUCKET_REGION: String = "gcs_bucket_region"
    const val CREDENTIAL: String = "credential"
    const val FORMAT: String = "format"
    const val KEEP_GCS_FILES: String = "keep_files_in_gcs-bucket"
    const val KEEP_GCS_FILES_VAL: String = "Keep all tmp files in GCS"
    const val DISABLE_TYPE_DEDUPE: String = "disable_type_dedupe"
    const val RAW_DATA_DATASET = "raw_data_dataset"
    const val NAMESPACE_PREFIX: String = "n"
}
