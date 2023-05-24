/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.utils;

import io.airbyte.db.factory.DatabaseDriver;
import java.util.Set;

public class DatabricksConstants {

  public static final String DATABRICKS_DATA_SOURCE_TYPE_KEY = "data_source_type";
  public static final String DATABRICKS_DATA_SOURCE_KEY = "data_source";
  public static final String DATABRICKS_SERVER_HOSTNAME_KEY = "databricks_server_hostname";
  public static final String DATABRICKS_HTTP_PATH_KEY = "databricks_http_path";
  public static final String DATABRICKS_PORT_KEY = "databricks_port";
  public static final String DATABRICKS_CATALOG_KEY = "database";
  public static final String DATABRICKS_SCHEMA_KEY = "schema";
  public static final String DATABRICKS_ENABLE_SCHEMA_EVOLUTION_KEY = "enable_schema_evolution";
  public static final String DATABRICKS_CATALOG_JDBC_KEY = "ConnCatalog";
  public static final String DATABRICKS_SCHEMA_JDBC_KEY = "ConnSchema";
  public static final String DATABRICKS_PURGE_STAGING_DATA_KEY = "purge_staging_data";
  public static final String DATABRICKS_PERSONAL_ACCESS_TOKEN_KEY = "databricks_personal_access_token";
  public static final String DATABRICKS_USERNAME = "token";
  public static final String DATABRICKS_DRIVER_CLASS = DatabaseDriver.DATABRICKS.getDriverClassName();

  public static final Set<String> DEFAULT_TBL_PROPERTIES = Set.of(
      "delta.autoOptimize.optimizeWrite = true",
      "delta.autoOptimize.autoCompact = true");

  private DatabricksConstants() {}

}
