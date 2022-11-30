/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;

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
  private final DatabricksStorageConfig storageConfig;

  public DatabricksDestinationConfig(final String databricksServerHostname,
                                     final String databricksHttpPath,
                                     final String databricksPort,
                                     final String databricksPersonalAccessToken,
                                     final String databaseSchema,
                                     final boolean purgeStagingData,
                                     DatabricksStorageConfig storageConfig) {
    this.databricksServerHostname = databricksServerHostname;
    this.databricksHttpPath = databricksHttpPath;
    this.databricksPort = databricksPort;
    this.databricksPersonalAccessToken = databricksPersonalAccessToken;
    this.databaseSchema = databaseSchema;
    this.purgeStagingData = purgeStagingData;
    this.storageConfig = storageConfig;
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
        DatabricksStorageConfig.getDatabricksStorageConfig(config.get("data_source")));
  }

  public String getDatabricksServerHostname() {
    return databricksServerHostname;
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

  public DatabricksStorageConfig getStorageConfig() {
    return storageConfig;
  }

}
