/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.mysql.MySQLSqlOperations.VersionCompatibility;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySQLDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySQLDestination.class);

  public static final String DATABASE_KEY = "database";
  public static final String HOST_KEY = "host";
  public static final String JDBC_URL_KEY = "jdbc_url";
  public static final String JDBC_URL_PARAMS_KEY = "jdbc_url_params";
  public static final String PASSWORD_KEY = "password";
  public static final String PORT_KEY = "port";
  public static final String SSL_KEY = "ssl";
  public static final String USERNAME_KEY = "username";

  public static final String DRIVER_CLASS = DatabaseDriver.MYSQL.getDriverClassName();

  static final Map<String, String> DEFAULT_JDBC_PARAMETERS = ImmutableMap.of(
      // zero dates by default cannot be parsed into java date objects (they will throw an error)
      // in addition, users don't always have agency in fixing them e.g: maybe they don't own the database
      // and can't
      // remove zero date values.
      // since zero dates are placeholders, we convert them to null by default
      "zeroDateTimeBehavior", "convertToNull",
      "allowLoadLocalInfile", "true");

  static final Map<String, String> DEFAULT_SSL_JDBC_PARAMETERS = MoreMaps.merge(ImmutableMap.of(
      "useSSL", "true",
      "requireSSL", "true",
      "verifyServerCertificate", "false"),
      DEFAULT_JDBC_PARAMETERS);

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new MySQLDestination(), List.of(HOST_KEY), List.of(PORT_KEY));
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try (final JdbcDatabase database = getDatabase(config)) {
      final MySQLSqlOperations mySQLSqlOperations = (MySQLSqlOperations) getSqlOperations();

      final String outputSchema = getNamingResolver().getIdentifier(config.get(DATABASE_KEY).asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, getNamingResolver(),
          mySQLSqlOperations);

      mySQLSqlOperations.verifyLocalFileEnabled(database);

      final VersionCompatibility compatibility = mySQLSqlOperations.isCompatibleVersion(database);
      if (!compatibility.isCompatible()) {
        throw new RuntimeException(String
            .format("Your MySQL version %s is not compatible with Airbyte",
                compatibility.getVersion()));
      }

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    }
  }

  public MySQLDestination() {
    super(DRIVER_CLASS, new MySQLNameTransformer(), new MySQLSqlOperations());
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    if (useSSL(config)) {
      return DEFAULT_SSL_JDBC_PARAMETERS;
    } else {
      return DEFAULT_JDBC_PARAMETERS;
    }
  }

  private boolean useSSL(final JsonNode config) {
    return !config.has(SSL_KEY) || config.get(SSL_KEY).asBoolean();
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String jdbcUrl = String.format("jdbc:mysql://%s:%s/%s",
        config.get(HOST_KEY).asText(),
        config.get(PORT_KEY).asText(),
        config.get(DATABASE_KEY).asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(USERNAME_KEY, config.get(USERNAME_KEY).asText())
        .put(JDBC_URL_KEY, jdbcUrl);

    if (config.has(PASSWORD_KEY)) {
      configBuilder.put(PASSWORD_KEY, config.get(PASSWORD_KEY).asText());
    }
    if (config.has(JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JDBC_URL_PARAMS_KEY, config.get(JDBC_URL_PARAMS_KEY));
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = MySQLDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", MySQLDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MySQLDestination.class);
  }

}
