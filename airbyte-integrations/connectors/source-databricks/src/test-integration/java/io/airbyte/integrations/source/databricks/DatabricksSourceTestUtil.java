package io.airbyte.integrations.source.databricks;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.commons.json.Jsons;
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

  public static JsonNode buildJdbcConfig(final JsonNode config) {
    final DatabricksSourceConfig databricksConfig = DatabricksSourceConfig.get(config);

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, DatabricksConstants.DATABRICKS_USERNAME)
        .put(JdbcUtils.PASSWORD_KEY, databricksConfig.personalAccessToken())
        .put(JdbcUtils.JDBC_URL_KEY, databricksConfig.getDatabricksConnectionString());
    return Jsons.jsonNode(configBuilder.build());
  }
}
