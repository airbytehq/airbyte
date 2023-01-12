/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.util.Map;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TiDBDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(TiDBDestination.class);
  public static final String DRIVER_CLASS = "com.mysql.cj.jdbc.Driver";

  static final Map<String, String> DEFAULT_JDBC_PARAMETERS = ImmutableMap.of(
      "allowLoadLocalInfile", "true");

  static final Map<String, String> DEFAULT_SSL_JDBC_PARAMETERS = MoreMaps.merge(ImmutableMap.of(
      "useSSL", "true",
      "requireSSL", "true",
      "verifyServerCertificate", "false"),
      DEFAULT_JDBC_PARAMETERS);

  public TiDBDestination() {
    super(DRIVER_CLASS, new TiDBSQLNameTransformer(), new TiDBSqlOperations());
  }

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new TiDBDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    final DataSource dataSource = getDataSource(config);

    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final String outputSchema = getNamingResolver().getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, getNamingResolver(), getSqlOperations());
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
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
  protected Map<String, String> getDefaultConnectionProperties(JsonNode config) {
    if (config.has(JdbcUtils.SSL_KEY) && config.get(JdbcUtils.SSL_KEY).asBoolean()) {
      return DEFAULT_SSL_JDBC_PARAMETERS;
    } else {
      return DEFAULT_JDBC_PARAMETERS;
    }
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asInt(),
        config.get(JdbcUtils.DATABASE_KEY).asText()));

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }
    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY));
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = TiDBDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", TiDBDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", TiDBDestination.class);
  }

}
