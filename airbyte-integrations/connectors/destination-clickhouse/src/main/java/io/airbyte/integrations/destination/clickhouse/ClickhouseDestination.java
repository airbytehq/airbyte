/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.CLICKHOUSE.getDriverClassName();

  static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      "socket_timeout", "3000000",
      JdbcUtils.SSL_KEY, "true",
      "sslmode", "none");

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new ClickhouseDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public ClickhouseDestination() {
    super(DRIVER_CLASS, new ClickhouseSQLNameTransformer(), new ClickhouseSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String jdbcUrl = String.format("jdbc:clickhouse://%s:%s/%s?",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final NamingConventionTransformer namingResolver = getNamingResolver();
      final String outputSchema = namingResolver.getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, namingResolver, getSqlOperations());
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
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
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    if (JdbcUtils.useSsl(config)) {
      return SSL_JDBC_PARAMETERS;
    } else {
      // No need for any parameters if the connection doesn't use SSL except socket_timeout
      return ImmutableMap.of("socket_timeout", "3000000");
    }
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = ClickhouseDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", ClickhouseDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ClickhouseDestination.class);
  }

}
