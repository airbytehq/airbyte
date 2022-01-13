/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file;

public class AzureConsts {

  public static final long BUTCH_SIZE = 4 * 1024 * 1024;

  public static final String LOADING_METHOD = "loading_method";
  public static final String METHOD = "method";
  public static final String CREDENTIAL = "credential";

  public static final String BUCKET_NAME = "bucket_name";
  public static final String BUCKET_PATH = "bucket_path";
  public static final String BUCKET_REGION = "bucket_region";

  public static final String GCS_STAGING = "GCS Staging";
  public static final String GCS_BUCKET_NAME = "gcs_bucket_name";
  public static final String GCS_BUCKET_PATH = "gcs_bucket_path";
  public static final String GCS_BUCKET_REGION = "gcs_bucket_region";

  public static final String S3_STAGING = "S3 Staging";
  public static final String S3_ENDPOINT = "s3_endpoint";
  public static final String S3_BUCKET_NAME = "s3_bucket_name";
  public static final String S3_BUCKET_PATH = "s3_bucket_path";
  public static final String S3_BUCKET_REGION = "s3_bucket_region";
  public static final String S3_ACCESS_KEY_ID = "access_key_id";
  public static final String S3_SECRET_ACCESS_KEY = "secret_access_key";

  public static final String FORMAT = "format";
  public static final String FORMAT_TYPE = "format_type";
  public static final String FORMAT_FLATTENING = "flattening";
  public static final String FORMAT_CSV = "CSV";

  public static final String KEEP_GCS_FILES = "keep_files_in_gcs-bucket";
  public static final String KEEP_GCS_FILES_VAL = "Keep all tmp files in GCS";

  public static final String KEEP_S3_FILES = "keep_files_in_s3-bucket";
  public static final String KEEP_S3_FILES_VAL = "Keep all tmp files in S3";

}
