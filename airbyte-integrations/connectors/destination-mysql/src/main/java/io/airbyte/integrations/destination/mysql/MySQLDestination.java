/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import static io.airbyte.integrations.base.errors.messages.ErrorMessage.getErrorMessage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.mysql.MySQLSqlOperations.VersionCompatibility;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.util.Map;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySQLDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySQLDestination.class);
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
    return new SshWrappedDestination(new MySQLDestination(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final MySQLSqlOperations mySQLSqlOperations = (MySQLSqlOperations) getSqlOperations();

      final String outputSchema = getNamingResolver().getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
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
    } catch (final ConnectionErrorException e) {
      final String message = getErrorMessage(e.getStateCode(), e.getErrorCode(), e.getExceptionMessage(), e);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(e, message);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(message);
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

  public MySQLDestination() {
    super(DRIVER_CLASS, new MySQLNameTransformer(), new MySQLSqlOperations());
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    if (JdbcUtils.useSsl(config)) {
      return DEFAULT_SSL_JDBC_PARAMETERS;
    } else {
      return DEFAULT_JDBC_PARAMETERS;
    }
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String jdbcUrl = String.format("jdbc:mysql://%s:%s/%s",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

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

  public static void main(final String[] args) throws Exception {
    final Destination destination = MySQLDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", MySQLDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MySQLDestination.class);
  }

}
