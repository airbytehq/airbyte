/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks.utils;

import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_CATALOG_JDBC_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_CATALOG_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_JDBC_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.source.databricks.DatabricksSourceConfig;
import java.util.HashMap;
import java.util.Map;
import javax.sql.DataSource;

public class DatabricksDatabaseUtil {

  public static String getDatabricksConnectionString(final DatabricksSourceConfig databricksConfig) {
    return String.format(DatabaseDriver.DATABRICKS.getUrlFormatString(),
        databricksConfig.serverHostname(),
        databricksConfig.port(),
        databricksConfig.httpPath());
  }

  public static DataSource getDataSource(final JsonNode config) {
    final Map<String, String> property = new HashMap<>();
    if (config.has(DATABRICKS_CATALOG_KEY)) {
      property.put(DATABRICKS_CATALOG_JDBC_KEY, config.get(DATABRICKS_CATALOG_KEY).asText());
    }
    if (config.has(DATABRICKS_SCHEMA_KEY)) {
      property.put(DATABRICKS_SCHEMA_JDBC_KEY, config.get(DATABRICKS_SCHEMA_KEY).asText());
    }
    final DatabricksSourceConfig databricksConfig = DatabricksSourceConfig.get(config);
    return DataSourceFactory.create(
        DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.personalAccessToken(),
        DatabricksConstants.DATABRICKS_DRIVER_CLASS,
        getDatabricksConnectionString(databricksConfig),
        property);
  }

}
