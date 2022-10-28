/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class YugabytedbDestination extends AbstractJdbcDestination {

  private static final Logger LOGGER = LoggerFactory.getLogger(YugabytedbDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.YUGABYTEDB.getDriverClassName();

  public YugabytedbDestination() {
    super(DRIVER_CLASS, new YugabytedbNamingTransformer(), new YugabytedbSqlOperations());
  }

  public static void main(String[] args) throws Exception {
    LOGGER.info("starting destination: {}", YugabytedbDestination.class);
    new IntegrationRunner(new YugabytedbDestination()).run(args);
    LOGGER.info("completed destination: {}", YugabytedbDestination.class);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(JsonNode config) {
    return Collections.emptyMap();
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    String schema =
        Optional.ofNullable(config.get(JdbcUtils.SCHEMA_KEY)).map(JsonNode::asText).orElse("public");

    String jdbcUrl = "jdbc:yugabytedb://" + config.get(JdbcUtils.HOST_KEY).asText() + ":"
        + config.get(JdbcUtils.PORT_KEY).asText() + "/"
        + config.get(JdbcUtils.DATABASE_KEY).asText();

    ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
        .put(JdbcUtils.SCHEMA_KEY, schema);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

}
