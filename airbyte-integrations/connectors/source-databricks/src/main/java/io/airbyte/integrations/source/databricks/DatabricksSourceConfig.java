/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks;

import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_CATALOG_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_ENABLE_SCHEMA_EVOLUTION_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_HTTP_PATH_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_PERSONAL_ACCESS_TOKEN_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_PORT_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_PURGE_STAGING_DATA_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SERVER_HOSTNAME_KEY;

import com.fasterxml.jackson.databind.JsonNode;

public record DatabricksSourceConfig(String serverHostname,
                                     String httpPath,
                                     String port,
                                     String personalAccessToken,
                                     String catalog,
                                     String schema,
                                     boolean isPurgeStagingData,
                                     boolean enableSchemaEvolution) {

  static final String DEFAULT_DATABRICKS_PORT = "443";
  static final String DEFAULT_DATABASE_SCHEMA = "tpch";
  static final String DEFAULT_CATALOG = "samples";
  static final boolean DEFAULT_PURGE_STAGING_DATA = true;
  static final boolean DEFAULT_ENABLE_SCHEMA_EVOLUTION = false;

  public static DatabricksSourceConfig get(final JsonNode config) {
    // Preconditions.checkArgument(
    // config.has("accept_terms") && config.get("accept_terms").asBoolean(),
    // "You must agree to the Databricks JDBC Terms & Conditions to use this connector");

    return new DatabricksSourceConfig(
        config.get(DATABRICKS_SERVER_HOSTNAME_KEY).asText(),
        config.get(DATABRICKS_HTTP_PATH_KEY).asText(),
        config.has(DATABRICKS_PORT_KEY) ? config.get(DATABRICKS_PORT_KEY).asText() : DEFAULT_DATABRICKS_PORT,
        config.get(DATABRICKS_PERSONAL_ACCESS_TOKEN_KEY).asText(),
        config.has(DATABRICKS_CATALOG_KEY) ? config.get(DATABRICKS_CATALOG_KEY).asText() : DEFAULT_CATALOG,
        config.has(DATABRICKS_SCHEMA_KEY) ? config.get(DATABRICKS_SCHEMA_KEY).asText() : DEFAULT_DATABASE_SCHEMA,
        config.has(DATABRICKS_ENABLE_SCHEMA_EVOLUTION_KEY) ? config.get(DATABRICKS_ENABLE_SCHEMA_EVOLUTION_KEY).asBoolean()
            : DEFAULT_ENABLE_SCHEMA_EVOLUTION,
        config.has(DATABRICKS_PURGE_STAGING_DATA_KEY) ? config.get(DATABRICKS_PURGE_STAGING_DATA_KEY).asBoolean() : DEFAULT_PURGE_STAGING_DATA);
  }

}
