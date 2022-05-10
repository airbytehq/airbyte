/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.mariadb_columnstore.MariadbColumnstoreSqlOperations.VersionCompatibility;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MariadbColumnstoreDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MariadbColumnstoreDestination.class);
  public static final String DRIVER_CLASS = DatabaseDriver.MARIADB.getDriverClassName();
  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");

  static final Map<String, String> DEFAULT_JDBC_PARAMETERS = ImmutableMap.of(
      "allowLoadLocalInfile", "true");

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new MariadbColumnstoreDestination(), HOST_KEY, PORT_KEY);
  }

  public MariadbColumnstoreDestination() {
    super(DRIVER_CLASS, new MariadbColumnstoreNameTransformer(), new MariadbColumnstoreSqlOperations());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final MariadbColumnstoreSqlOperations mariadbColumnstoreSqlOperations = (MariadbColumnstoreSqlOperations) getSqlOperations();
      final String outputSchema = getNamingResolver().getIdentifier(config.get("database").asText());

      final VersionCompatibility compatibility = mariadbColumnstoreSqlOperations.isCompatibleVersion(database);
      if (!compatibility.isCompatible()) {
        throw new RuntimeException(String
            .format("Your MariaDB Columnstore version %s is not compatible with Airbyte",
                compatibility.getVersion()));
      }

      mariadbColumnstoreSqlOperations.verifyLocalFileEnabled(database);

      attemptSQLCreateAndDropTableOperations(
          outputSchema,
          database,
          getNamingResolver(),
          mariadbColumnstoreSqlOperations);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    } finally {
      try {
        DataSourceFactory.close(dataSource);
      } catch (final IOException e) {
        LOGGER.warn("Unable to close data source.", e);
      }
    }

    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return DEFAULT_JDBC_PARAMETERS;
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final String jdbcUrl = String.format(DatabaseDriver.MARIADB.getUrlFormatString(),
        config.get("host").asText(),
        config.get("port").asInt(),
        config.get("database").asText());

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbcUrl);

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = MariadbColumnstoreDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", MariadbColumnstoreDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MariadbColumnstoreDestination.class);
  }

}
