/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.CLICKHOUSE.getDriverClassName();

  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");

  private static final String PASSWORD = "password";

  static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      "ssl", "true",
      "sslmode", "none");

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new ClickhouseDestination(), HOST_KEY, PORT_KEY);
  }

  public ClickhouseDestination() {
    super(DRIVER_CLASS, new ClickhouseSQLNameTransformer(), new ClickhouseSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String jdbcUrl = String.format("jdbc:clickhouse://%s:%s/%s?",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbcUrl);

    if (config.has(PASSWORD)) {
      configBuilder.put(PASSWORD, config.get(PASSWORD).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  private boolean useSsl(final JsonNode config) {
    return !config.has("ssl") || config.get("ssl").asBoolean();
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try (final JdbcDatabase database = getDatabase(config)) {
      final NamingConventionTransformer namingResolver = getNamingResolver();
      final String outputSchema = namingResolver.getIdentifier(config.get("database").asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, namingResolver, getSqlOperations());
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    }
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    if (useSsl(config)) {
      return SSL_JDBC_PARAMETERS;
    } else {
      // No need for any parameters if the connection doesn't use SSL
      return new HashMap<>();
    }
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = ClickhouseDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", ClickhouseDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ClickhouseDestination.class);
  }

}
