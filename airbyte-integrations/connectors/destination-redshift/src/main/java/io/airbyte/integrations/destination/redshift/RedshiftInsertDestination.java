/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import java.util.Map;
import java.util.Optional;

public class RedshiftInsertDestination extends AbstractJdbcDestination {

  private static final String DRIVER_CLASS = DatabaseDriver.REDSHIFT.getDriverClassName();
  private static final String USERNAME = "username";
  private static final String PASSWORD = "password";
  private static final String SCHEMA = "schema";
  private static final String JDBC_URL = "jdbc_url";

  public static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      "ssl", "true",
      "sslfactory", "com.amazon.redshift.ssl.NonValidatingFactory");

  public RedshiftInsertDestination(final RedshiftDataTmpTableMode redshiftDataTmpTableMode) {
    super(DRIVER_CLASS, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations(redshiftDataTmpTableMode));
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode redshiftConfig) {
    return getJdbcConfig(redshiftConfig);
  }

  @Override
  public JdbcDatabase getDatabase(final JsonNode config) {
    return getJdbcDatabase(config);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return SSL_JDBC_PARAMETERS;
  }

  public static JdbcDatabase getJdbcDatabase(final JsonNode config) {
    final var jdbcConfig = RedshiftInsertDestination.getJdbcConfig(config);
    return new DefaultJdbcDatabase(
        DataSourceFactory.create(
        jdbcConfig.get(USERNAME).asText(),
        jdbcConfig.has(PASSWORD) ? jdbcConfig.get(PASSWORD).asText() : null,
        RedshiftInsertDestination.DRIVER_CLASS,
        jdbcConfig.get(JDBC_URL).asText(),
        SSL_JDBC_PARAMETERS)
    );
  }

  public static JsonNode getJdbcConfig(final JsonNode redshiftConfig) {
    final String schema = Optional.ofNullable(redshiftConfig.get(SCHEMA)).map(JsonNode::asText).orElse("public");
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(USERNAME, redshiftConfig.get(USERNAME).asText())
        .put(PASSWORD, redshiftConfig.get(PASSWORD).asText())
        .put(JDBC_URL, String.format("jdbc:redshift://%s:%s/%s",
            redshiftConfig.get("host").asText(),
            redshiftConfig.get("port").asText(),
            redshiftConfig.get("database").asText()))
        .put(SCHEMA, schema)
        .build());
  }

}
