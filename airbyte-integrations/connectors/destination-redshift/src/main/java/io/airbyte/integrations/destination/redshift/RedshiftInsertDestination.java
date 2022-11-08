/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import java.util.Map;
import java.util.Optional;
import javax.sql.DataSource;

public class RedshiftInsertDestination extends AbstractJdbcDestination {

  public static final String DRIVER_CLASS = DatabaseDriver.REDSHIFT.getDriverClassName();
  public static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      JdbcUtils.SSL_KEY, "true",
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
        jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        RedshiftInsertDestination.DRIVER_CLASS,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
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
    final String schema = Optional.ofNullable(redshiftConfig.get(JdbcUtils.SCHEMA_KEY)).map(JsonNode::asText).orElse("public");
    Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, redshiftConfig.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.PASSWORD_KEY, redshiftConfig.get(JdbcUtils.PASSWORD_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, String.format("jdbc:redshift://%s:%s/%s",
            redshiftConfig.get(JdbcUtils.HOST_KEY).asText(),
            redshiftConfig.get(JdbcUtils.PORT_KEY).asText(),
            redshiftConfig.get(JdbcUtils.DATABASE_KEY).asText()))
        .put(JdbcUtils.SCHEMA_KEY, schema);

    if (redshiftConfig.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, redshiftConfig.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
    }

    return Jsons.jsonNode(configBuilder.build());
  }

}
