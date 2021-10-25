/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Preconditions;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetFormatConfig;

/**
 * Currently only S3 is supported. So the data source config is always {@link S3DestinationConfig}.
 */
public class DatabricksDestinationConfig {

  static final String DEFAULT_DATABRICKS_PORT = "443";
  static final String DEFAULT_DATABASE_SCHEMA = "public";
  static final boolean DEFAULT_PURGE_STAGING_DATA = true;

  private final String databricksServerHostname;
  private final String databricksHttpPath;
  private final String databricksPort;
  private final String databricksPersonalAccessToken;
  private final String databaseSchema;
  private final boolean purgeStagingData;
  private final S3DestinationConfig s3DestinationConfig;

  public DatabricksDestinationConfig(final String databricksServerHostname,
                                     final String databricksHttpPath,
                                     final String databricksPort,
                                     final String databricksPersonalAccessToken,
                                     final String databaseSchema,
                                     final boolean purgeStagingData,
                                     final S3DestinationConfig s3DestinationConfig) {
    this.databricksServerHostname = databricksServerHostname;
    this.databricksHttpPath = databricksHttpPath;
    this.databricksPort = databricksPort;
    this.databricksPersonalAccessToken = databricksPersonalAccessToken;
    this.databaseSchema = databaseSchema;
    this.purgeStagingData = purgeStagingData;
    this.s3DestinationConfig = s3DestinationConfig;
  }

  public static DatabricksDestinationConfig get(final JsonNode config) {
    Preconditions.checkArgument(
        config.has("accept_terms") && config.get("accept_terms").asBoolean(),
        "You must agree to the Databricks JDBC Terms & Conditions to use this connector");

    return new DatabricksDestinationConfig(
        config.get("databricks_server_hostname").asText(),
        config.get("databricks_http_path").asText(),
        config.has("databricks_port") ? config.get("databricks_port").asText() : DEFAULT_DATABRICKS_PORT,
        config.get("databricks_personal_access_token").asText(),
        config.has("database_schema") ? config.get("database_schema").asText() : DEFAULT_DATABASE_SCHEMA,
        config.has("purge_staging_data") ? config.get("purge_staging_data").asBoolean() : DEFAULT_PURGE_STAGING_DATA,
        getDataSource(config.get("data_source")));
  }

  public static S3DestinationConfig getDataSource(final JsonNode dataSource) {
    return new S3DestinationConfig(
        "",
        dataSource.get("s3_bucket_name").asText(),
        dataSource.get("s3_bucket_path").asText(),
        dataSource.get("s3_bucket_region").asText(),
        dataSource.get("s3_access_key_id").asText(),
        dataSource.get("s3_secret_access_key").asText(),
        getDefaultParquetConfig());
  }

  public String getDatabricksServerHostname() {
    return databricksServerHostname;
  }

  private static S3ParquetFormatConfig getDefaultParquetConfig() {
    return new S3ParquetFormatConfig(new ObjectMapper().createObjectNode());
  }

  public String getDatabricksHttpPath() {
    return databricksHttpPath;
  }

  public String getDatabricksPort() {
    return databricksPort;
  }

  public String getDatabricksPersonalAccessToken() {
    return databricksPersonalAccessToken;
  }

  public String getDatabaseSchema() {
    return databaseSchema;
  }

  public boolean isPurgeStagingData() {
    return purgeStagingData;
  }

  public S3DestinationConfig getS3DestinationConfig() {
    return s3DestinationConfig;
  }

}
