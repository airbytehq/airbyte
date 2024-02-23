/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.DISABLE;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_MODE;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_SSL;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_SSL_MODE;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.obtainConnectionOptions;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.postgres.typing_deduping.PostgresSqlGenerator;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new PostgresDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public PostgresDestination() {
    super(DRIVER_CLASS, new PostgresSQLNameTransformer(), new PostgresSqlOperations());
  }

  @Override
  protected DataSourceFactory.DataSourceBuilder modifyDataSourceBuilder(final DataSourceFactory.DataSourceBuilder builder) {
    // Anything in the pg_temp schema is only visible to the connection that created it.
    // So this creates an airbyte_safe_cast function that only exists for the duration of
    // a single connection.
    // This avoids issues with creating the same function concurrently (e.g. if multiple syncs run
    // at the same time).
    // Function definition copied from https://dba.stackexchange.com/a/203986

    // Adding 60 seconds to connection timeout, for ssl connections, default 10 seconds is not enough
    return builder.withConnectionTimeout(Duration.ofSeconds(60))
        .withConnectionInitSql("""
                               CREATE FUNCTION pg_temp.airbyte_safe_cast(_in text, INOUT _out ANYELEMENT)
                                 LANGUAGE plpgsql AS
                               $func$
                               BEGIN
                                 EXECUTE format('SELECT %L::%s', $1, pg_typeof(_out))
                                 INTO  _out;
                               EXCEPTION WHEN others THEN
                                 -- do nothing: _out already carries default
                               END
                               $func$;
                               """);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (!config.has(PARAM_SSL) || config.get(PARAM_SSL).asBoolean()) {
      if (config.has(PARAM_SSL_MODE)) {
        if (DISABLE.equals(config.get(PARAM_SSL_MODE).get(PARAM_MODE).asText())) {
          additionalParameters.put("sslmode", DISABLE);
        } else {
          additionalParameters.putAll(obtainConnectionOptions(config.get(PARAM_SSL_MODE)));
        }
      } else {
        additionalParameters.put(JdbcUtils.SSL_KEY, "true");
        additionalParameters.put("sslmode", "require");
      }
    }
    return additionalParameters;
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String schema = Optional.ofNullable(config.get(JdbcUtils.SCHEMA_KEY)).map(JsonNode::asText).orElse("public");

    String encodedDatabase = config.get(JdbcUtils.DATABASE_KEY).asText();
    if (encodedDatabase != null) {
      try {
        encodedDatabase = URLEncoder.encode(encodedDatabase, "UTF-8");
      } catch (final UnsupportedEncodingException e) {
        // Should never happen
        e.printStackTrace();
      }
    }
    final String jdbcUrl = String.format("jdbc:postgresql://%s:%s/%s?",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        encodedDatabase);

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
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

  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return new PostgresSqlGenerator(new PostgresSQLNameTransformer());
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = PostgresDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", PostgresDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", PostgresDestination.class);
  }

}
