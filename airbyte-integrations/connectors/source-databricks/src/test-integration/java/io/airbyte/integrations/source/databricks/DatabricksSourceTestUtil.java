package io.airbyte.integrations.source.databricks;

import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_CATALOG_JDBC_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_CATALOG_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_JDBC_KEY;
import static io.airbyte.integrations.source.databricks.utils.DatabricksConstants.DATABRICKS_SCHEMA_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.databricks.utils.DatabricksConstants;
import java.util.HashMap;
import javax.sql.DataSource;

public class DatabricksSourceTestUtil {

  public static DataSource createDataSource(JsonNode config) {
    final DatabricksSourceConfig databricksConfig = DatabricksSourceConfig.get(config);

    return DataSourceFactory.create(
        DatabricksConstants.DATABRICKS_USERNAME,
        databricksConfig.personalAccessToken(),
        DatabricksSource.DRIVER_CLASS,
        databricksConfig.getDatabricksConnectionString(),
        new HashMap<String, String>());
  }

  protected static String buildConnectionProperty(JsonNode config, String key, String jdbcKey) {
    return config.has(key) ? jdbcKey + "=" + config.get(key).asText().toLowerCase() : "";
  }

  public static JsonNode buildJdbcConfig(final JsonNode config) {
    final DatabricksSourceConfig databricksConfig = DatabricksSourceConfig.get(config);

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, DatabricksConstants.DATABRICKS_USERNAME)
        .put(JdbcUtils.PASSWORD_KEY, databricksConfig.personalAccessToken())
        .put(JdbcUtils.JDBC_URL_KEY, databricksConfig.getDatabricksConnectionString());

    StringBuilder connectionProperties = new StringBuilder();
    connectionProperties.append(buildConnectionProperty(config, DATABRICKS_CATALOG_KEY, DATABRICKS_CATALOG_JDBC_KEY));
    connectionProperties.append(buildConnectionProperty(config, DATABRICKS_SCHEMA_KEY, JdbcUtils.AMPERSAND + DATABRICKS_SCHEMA_JDBC_KEY));

    if (connectionProperties.length() > 0) {
      configBuilder.put(JdbcUtils.CONNECTION_PROPERTIES_KEY, connectionProperties.toString());
    }
    return Jsons.jsonNode(configBuilder.build());
  }
}
