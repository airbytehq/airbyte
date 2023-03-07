/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.constant;

public final class S3Constants {

  public static final String S_3_BUCKET_PATH = "s3_bucket_path";
  public static final String FILE_NAME_PATTERN = "file_name_pattern";
  public static final String S_3_PATH_FORMAT = "s3_path_format";
  public static final String S_3_ENDPOINT = "s3_endpoint";
  public static final String ACCESS_KEY_ID = "access_key_id";
  public static final String S_3_ACCESS_KEY_ID = "s3_access_key_id";
  public static final String S_3_SECRET_ACCESS_KEY = "s3_secret_access_key";
  public static final String SECRET_ACCESS_KEY = "secret_access_key";
  public static final String S_3_BUCKET_NAME = "s3_bucket_name";
  public static final String S_3_BUCKET_REGION = "s3_bucket_region";

  // r2 requires account_id
  public static final String ACCOUNT_ID = "account_id";

  private S3Constants() {}

}
