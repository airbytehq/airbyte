/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bytehouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;

import org.apache.http.util.TextUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BytehouseDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BytehouseDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.BYTEHOUSE.getDriverClassName();
  public static final String DEFAULT_USERNAME = "bytehouse";
  public static final List<String> DEFAULT_PARAMETERS = ImmutableList.of("user="+DEFAULT_USERNAME, "secure=true");

  public BytehouseDestination() {
    super(DRIVER_CLASS, new BytehouseSQLNameTransformer(), new BytehouseSqlOperations());
  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new BytehouseDestination()).run(args);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    DataSource dataSource;
    try {
      dataSource = getDataSource(config);
    } catch (Exception e) {
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not getDataSource: " + e.getMessage());
    }
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final NamingConventionTransformer namingResolver = getNamingResolver();
      final String outputSchema = namingResolver.getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
      attemptTableOperations(outputSchema, database, namingResolver, getSqlOperations(), true);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final Exception e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(JsonNode config) {
    return Collections.emptyMap();
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(
        String.format(DatabaseDriver.BYTEHOUSE.getUrlFormatString(),
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()));

    var params = new ArrayList<>(DEFAULT_PARAMETERS);
    params.add("api_key=" + config.get(API_KEY).asText());
    jdbcUrl.append("?").append(String.join("&", params));

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, DEFAULT_USERNAME)
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

//    rewriteUrlParams(config);
    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  public static final String API_KEY = "api_key";
  public static void rewriteUrlParams(JsonNode config) {
    String apiKey = config.get(API_KEY).asText();

    String extraParams = String.format("api_key=%s&secure=true", apiKey);
    if (!config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      ((ObjectNode)config).put(JdbcUtils.JDBC_URL_PARAMS_KEY, extraParams);
      return;
    }

    String urlParams = config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText();
    if (TextUtils.isBlank(urlParams)) {
      ((ObjectNode)config).put(JdbcUtils.JDBC_URL_PARAMS_KEY, extraParams);
    } else {
      ((ObjectNode)config).put(JdbcUtils.JDBC_URL_PARAMS_KEY, urlParams + "&" + extraParams);
    }
  }

}
