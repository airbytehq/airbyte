/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.DISABLE;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_MODE;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_SSL;
import static io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils.PARAM_SSL_MODE;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.destination.postgres.typing_deduping.PostgresDataTransformer;
import io.airbyte.integrations.destination.postgres.typing_deduping.PostgresDestinationHandler;
import io.airbyte.integrations.destination.postgres.typing_deduping.PostgresRawTableAirbyteMetaMigration;
import io.airbyte.integrations.destination.postgres.typing_deduping.PostgresSqlGenerator;
import io.airbyte.integrations.destination.postgres.typing_deduping.PostgresState;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.postgresql.util.PSQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresDestination extends AbstractJdbcDestination<PostgresState> implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();

  private static final String DROP_CASCADE_OPTION = "drop_cascade";

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
          additionalParameters.putAll(PostgresSslConnectionUtils.obtainConnectionOptions(config.get(PARAM_SSL_MODE)));
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
      encodedDatabase = URLEncoder.encode(encodedDatabase, StandardCharsets.UTF_8);
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
  protected JdbcSqlGenerator getSqlGenerator(final JsonNode config) {
    final JsonNode dropCascadeNode = config.get(DROP_CASCADE_OPTION);
    final boolean dropCascade = dropCascadeNode != null && dropCascadeNode.asBoolean();
    return new PostgresSqlGenerator(new PostgresSQLNameTransformer(), dropCascade);
  }

  @Override
  protected JdbcDestinationHandler<PostgresState> getDestinationHandler(String databaseName, JdbcDatabase database, String rawTableSchema) {
    return new PostgresDestinationHandler(databaseName, database, rawTableSchema);
  }

  @Override
  protected List<Migration<PostgresState>> getMigrations(JdbcDatabase database,
                                                         String databaseName,
                                                         SqlGenerator sqlGenerator,
                                                         DestinationHandler<PostgresState> destinationHandler) {
    return List.of(new PostgresRawTableAirbyteMetaMigration(database, databaseName));
  }

  @Override
  protected StreamAwareDataTransformer getDataTransformer(ParsedCatalog parsedCatalog, String defaultNamespace) {
    return new PostgresDataTransformer();
  }

  @Override
  public boolean isV2Destination() {
    return true;
  }

  public static void main(final String[] args) throws Exception {
    AirbyteExceptionHandler.addThrowableForDeinterpolation(PSQLException.class);
    final Destination destination = PostgresDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", PostgresDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", PostgresDestination.class);
  }

}
