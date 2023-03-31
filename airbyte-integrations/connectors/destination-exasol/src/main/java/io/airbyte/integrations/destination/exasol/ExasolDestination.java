/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import java.util.HashMap;
import java.util.Map;

public class ExasolDestination extends AbstractJdbcDestination implements Destination {

  public static final String DRIVER_CLASS = DatabaseDriver.EXASOL.getDriverClassName();

  public ExasolDestination() {
    super(DRIVER_CLASS, new ExasolSQLNameTransformer(), new ExasolSqlOperations());
  }

  public static void main(String[] args) throws Exception {
    new IntegrationRunner(new ExasolDestination()).run(args);
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String jdbcUrl = String.format(DatabaseDriver.EXASOL.getUrlFormatString(),
        config.get(JdbcUtils.HOST_KEY).asText(), config.get(JdbcUtils.PORT_KEY).asInt());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
        .put("schema", config.get(JdbcUtils.SCHEMA_KEY).asText());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    Map<String, String> properties = new HashMap<>();
    properties.put("autocommit", "0");
    if (config.has("certificateFingerprint")) {
      properties.put("fingerprint", config.get("certificateFingerprint").asText());
    }
    return properties;
  }

}
