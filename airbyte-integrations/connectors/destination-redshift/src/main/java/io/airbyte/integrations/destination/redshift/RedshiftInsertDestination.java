/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import java.util.Map;
import java.util.Optional;
import javax.sql.DataSource;

public class RedshiftInsertDestination extends AbstractJdbcDestination {

  public static final String DRIVER_CLASS = DatabaseDriver.REDSHIFT.getDriverClassName();
  public static final String USERNAME = "username";
  public static final String PASSWORD = "password";
  public static final String JDBC_URL = "jdbc_url";
  private static final String SCHEMA = "schema";

  public static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      "ssl", "true",
      "sslfactory", "com.amazon.redshift.ssl.NonValidatingFactory");

  public RedshiftInsertDestination() {
    super(DRIVER_CLASS, new RedshiftSQLNameTransformer(), new RedshiftSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode redshiftConfig) {
    return getJdbcConfig(redshiftConfig);
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    final var jdbcConfig = getJdbcConfig(config);
    return DataSourceFactory.create(
        jdbcConfig.get(USERNAME).asText(),
        jdbcConfig.has(PASSWORD) ? jdbcConfig.get(PASSWORD).asText() : null,
        RedshiftInsertDestination.DRIVER_CLASS,
        jdbcConfig.get(JDBC_URL).asText(),
        SSL_JDBC_PARAMETERS);
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return SSL_JDBC_PARAMETERS;
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
