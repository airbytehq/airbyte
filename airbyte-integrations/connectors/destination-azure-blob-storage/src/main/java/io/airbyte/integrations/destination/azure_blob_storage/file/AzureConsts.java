/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.file;

public class AzureConsts {

  public static final int MiB = 1024 * 1024;

  public static final String LOADING_METHOD = "loading_method";
  public static final String METHOD = "method";
  public static final String GCS_STAGING = "GCS Staging";
  public static final String GCS_BUCKET_NAME = "gcs_bucket_name";
  public static final String GCS_BUCKET_PATH = "gcs_bucket_path";
  public static final String GCS_BUCKET_REGION = "gcs_bucket_region";
  public static final String CREDENTIAL = "credential";

  public static final String FORMAT = "format";
  public static final String FORMAT_TYPE = "format_type";
  public static final String FORMAT_CSV = "CSV";
  public static final String FORMAT_JSONL = "JSONL";

  public static final String KEEP_GCS_FILES = "keep_files_in_gcs-bucket";
  public static final String KEEP_GCS_FILES_VAL = "Keep all tmp files in GCS";

}
