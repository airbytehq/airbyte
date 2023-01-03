/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

public class BigQueryConsts {

  public static final int MiB = 1024 * 1024;
  public static final String CONFIG_DATASET_ID = "dataset_id";
  public static final String CONFIG_PROJECT_ID = "project_id";
  public static final String CONFIG_DATASET_LOCATION = "dataset_location";
  public static final String CONFIG_CREDS = "credentials_json";
  public static final String BIG_QUERY_CLIENT_CHUNK_SIZE = "big_query_client_buffer_size_mb";

  public static final String LOADING_METHOD = "loading_method";
  public static final String METHOD = "method";
  public static final String GCS_STAGING = "GCS Staging";
  public static final String GCS_BUCKET_NAME = "gcs_bucket_name";
  public static final String GCS_BUCKET_PATH = "gcs_bucket_path";
  public static final String GCS_BUCKET_REGION = "gcs_bucket_region";
  public static final String CREDENTIAL = "credential";
  public static final String FORMAT = "format";
  public static final String KEEP_GCS_FILES = "keep_files_in_gcs-bucket";
  public static final String KEEP_GCS_FILES_VAL = "Keep all tmp files in GCS";

  public static final String NAMESPACE_PREFIX = "n";

  // tests
  public static final String BIGQUERY_BASIC_CONFIG = "basic_bigquery_config";
  public static final String GCS_CONFIG = "gcs_config";

  public static final String CREDENTIAL_TYPE = "credential_type";
  public static final String HMAC_KEY_ACCESS_ID = "hmac_key_access_id";
  public static final String HMAC_KEY_ACCESS_SECRET = "hmac_key_secret";

}
