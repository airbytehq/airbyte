/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

/**
 * @author Leibniz on 2022/10/26.
 */
public class IcebergConstants {

  /**
   * Root Config keys
   */
  public static final String ICEBERG_CATALOG_CONFIG_KEY = "catalog_config";
  public static final String ICEBERG_STORAGE_CONFIG_KEY = "storage_config";
  public static final String ICEBERG_FORMAT_CONFIG_KEY = "format_config";

  /**
   * Catalog Config keys
   */
  public static final String ICEBERG_CATALOG_TYPE_CONFIG_KEY = "catalog_type";
  public static final String HIVE_THRIFT_URI_CONFIG_KEY = "hive_thrift_uri";
  public static final String DEFAULT_DATABASE_CONFIG_KEY = "database";
  public static final String JDBC_URL_CONFIG_KEY = "jdbc_url";
  public static final String JDBC_USERNAME_CONFIG_KEY = "username";
  public static final String JDBC_PASSWORD_CONFIG_KEY = "password";
  public static final String JDBC_SSL_CONFIG_KEY = "ssl";
  public static final String JDBC_CATALOG_SCHEMA_CONFIG_KEY = "catalog_schema";
  public static final String REST_CATALOG_URI_CONFIG_KEY = "rest_uri";
  public static final String REST_CATALOG_CREDENTIAL_CONFIG_KEY = "rest_credential";
  public static final String REST_CATALOG_TOKEN_CONFIG_KEY = "rest_token";

  /**
   * Storage Config keys
   */
  public static final String ICEBERG_STORAGE_TYPE_CONFIG_KEY = "storage_type";
  public static final String S3_ACCESS_KEY_ID_CONFIG_KEY = "access_key_id";
  public static final String S3_SECRET_KEY_CONFIG_KEY = "secret_access_key";
  public static final String S3_WAREHOUSE_URI_CONFIG_KEY = "s3_warehouse_uri";
  public static final String S3_BUCKET_REGION_CONFIG_KEY = "s3_bucket_region";
  public static final String S3_ENDPOINT_CONFIG_KEY = "s3_endpoint";
  public static final String S3_PATH_STYLE_ACCESS_CONFIG_KEY = "s3_path_style_access";
  public static final String MANAGED_WAREHOUSE_NAME = "managed_warehouse_name";

  /**
   * Format Config keys
   */
  public static final String FORMAT_TYPE_CONFIG_KEY = "format";
  public static final String FLUSH_BATCH_SIZE_CONFIG_KEY = "flush_batch_size";
  public static final String AUTO_COMPACT_CONFIG_KEY = "auto_compact";
  public static final String COMPACT_TARGET_FILE_SIZE_IN_MB_CONFIG_KEY = "compact_target_file_size_in_mb";

  /**
   * default values
   */
  public static final String CATALOG_NAME = "iceberg";
  public static final String DEFAULT_DATABASE = "default";

  /**
   * constant for QA checks to ignore http endpoint
   */
  public static final String HTTP_PREFIX = "http://"; // # ignore-https-check

}
