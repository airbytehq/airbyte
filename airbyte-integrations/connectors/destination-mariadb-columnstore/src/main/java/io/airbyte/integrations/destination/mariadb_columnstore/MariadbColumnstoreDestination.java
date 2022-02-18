/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.ssh.SshWrappedDestination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.mariadb_columnstore.MariadbColumnstoreSqlOperations.VersionCompatibility;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MariadbColumnstoreDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MariadbColumnstoreDestination.class);
  public static final String DRIVER_CLASS = "org.mariadb.jdbc.Driver";
  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");

  public static Destination sshWrappedDestination() {
    return new SshWrappedDestination(new MariadbColumnstoreDestination(), HOST_KEY, PORT_KEY);
  }

  public MariadbColumnstoreDestination() {
    super(DRIVER_CLASS, new MariadbColumnstoreNameTransformer(), new MariadbColumnstoreSqlOperations());
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (final JdbcDatabase database = getDatabase(config)) {
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
    }

    return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
  }

  @Override
  protected JdbcDatabase getDatabase(final JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);

    return Databases.createJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        getDriverClass(),
        "allowLoadLocalInfile=true");
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mariadb://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbcUrl.toString());

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = MariadbColumnstoreDestination.sshWrappedDestination();
    LOGGER.info("starting destination: {}", MariadbColumnstoreDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MariadbColumnstoreDestination.class);
  }

}
