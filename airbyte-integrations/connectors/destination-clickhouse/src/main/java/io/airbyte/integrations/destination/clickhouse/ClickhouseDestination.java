/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
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
import java.util.Collections;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.CLICKHOUSE.getDriverClassName();

  public static final String HTTPS_PROTOCOL = "https";
  public static final String HTTP_PROTOCOL = "http";

  static final List<String> SSL_PARAMETERS = ImmutableList.of(
      "socket_timeout=3000000",
      "sslmode=NONE");
  static final List<String> DEFAULT_PARAMETERS = ImmutableList.of(
      "socket_timeout=3000000");


  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new ClickhouseDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public ClickhouseDestination() {
    super(DRIVER_CLASS, new ClickhouseSQLNameTransformer(), new ClickhouseSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final boolean isSsl = JdbcUtils.useSsl(config);
    final StringBuilder jdbcUrl = new StringBuilder(
        String.format(DatabaseDriver.CLICKHOUSE.getUrlFormatString(),
            isSsl ? HTTPS_PROTOCOL : HTTP_PROTOCOL,
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt(),
            config.get(JdbcUtils.DATABASE_KEY).asText()));

    if (isSsl) {
      jdbcUrl.append("?").append(String.join("&", SSL_PARAMETERS));
    } else {
      jdbcUrl.append("?").append(String.join("&", DEFAULT_PARAMETERS));
    }

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
    return Collections.emptyMap();
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = ClickhouseDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", ClickhouseDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ClickhouseDestination.class);
  }

}
