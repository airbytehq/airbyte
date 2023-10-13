/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks;

import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_CATALOG_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_HTTP_PATH_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_PERSONAL_ACCESS_TOKEN_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_PORT_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SERVER_HOSTNAME_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.databricks.utils.DatabricksConstants;
import java.util.HashMap;
import java.util.Map;

public record DatabricksSourceConfig(String serverHostname,
                                     String httpPath,
                                     String port,
                                     String personalAccessToken,
                                     String catalog,
                                     String schema,
                                     String jdbcUrlParams) {

  static final String DEFAULT_DATABRICKS_PORT = "443/default";
  static final String DEFAULT_JDBC_URL_PARAMS = "";

  public String getDatabricksConnectionString() {
    String jdbcUrl =  String.format(DatabaseDriver.DATABRICKS.getUrlFormatString(),
        serverHostname(),
        port(),
        httpPath());

    jdbcUrl = String.format(jdbcUrl+DatabricksConstants.DATABRICKS_JDBC_URL_PARAMS_SEPARATOR+DatabricksConstants.DATABRICKS_CATALOG_JDBC_KEY+"=%s", catalog());
    if(schema() != null && !schema().isBlank()) {
      jdbcUrl = String.format(jdbcUrl+DatabricksConstants.DATABRICKS_JDBC_URL_PARAMS_SEPARATOR + DatabricksConstants.DATABRICKS_SCHEMA_JDBC_KEY + "=%s", schema());
    }
    if(!jdbcUrlParams().isBlank()) {
      String[] pairs = jdbcUrlParams().split(DatabricksConstants.DATABRICKS_JDBC_URL_PARAMS_SEPARATOR);
      String[] addedParams = {DatabricksConstants.DATABRICKS_CATALOG_JDBC_KEY, DatabricksConstants.DATABRICKS_SCHEMA_JDBC_KEY};
      for (String pair : pairs) {
        String[] keyValue = pair.split(JdbcUtils.EQUALS);

        if (keyValue.length == 2) {
          String key = keyValue[0].trim();
          String value = keyValue[1].trim();
          if (!key.contentEquals(DatabricksConstants.DATABRICKS_CATALOG_JDBC_KEY) && !key.contentEquals(DatabricksConstants.DATABRICKS_SCHEMA_JDBC_KEY)) {
            jdbcUrl = String.format(jdbcUrl + DatabricksConstants.DATABRICKS_JDBC_URL_PARAMS_SEPARATOR+"%s=%s",key, value);
          }
        }
      }

    }
    return jdbcUrl;
  }
  public static DatabricksSourceConfig get(final JsonNode config) {
    return new DatabricksSourceConfig(
        config.get(DATABRICKS_SERVER_HOSTNAME_KEY).asText(),
        config.get(DATABRICKS_HTTP_PATH_KEY).asText(),
        config.has(DATABRICKS_PORT_KEY) ? config.get(DATABRICKS_PORT_KEY).asText() : DEFAULT_DATABRICKS_PORT,
        config.get(DATABRICKS_PERSONAL_ACCESS_TOKEN_KEY).asText(),
        config.get(DATABRICKS_CATALOG_KEY).asText(),
        config.has(DATABRICKS_SCHEMA_KEY) ? config.get(DATABRICKS_SCHEMA_KEY).asText() : null,
        config.has(JdbcUtils.JDBC_URL_PARAMS_KEY) ? config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText() : DEFAULT_JDBC_URL_PARAMS);
  }

}
