/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.mysql.MySQLSqlOperations.VersionCompatibility;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySQLDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySQLDestination.class);

  public static final String DRIVER_CLASS = "com.mysql.cj.jdbc.Driver";

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (final JdbcDatabase database = getDatabase(config)) {
      MySQLSqlOperations mySQLSqlOperations = (MySQLSqlOperations) getSqlOperations();

      String outputSchema = getNamingResolver().getIdentifier(config.get("database").asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, getNamingResolver(),
          mySQLSqlOperations);

      mySQLSqlOperations.verifyLocalFileEnabled(database);

      VersionCompatibility compatibility = mySQLSqlOperations.isCompatibleVersion(database);
      if (!compatibility.isCompatible()) {
        throw new RuntimeException(String
            .format("Your MySQL version %s is not compatible with Airbyte",
                compatibility.getVersion()));
      }

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
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
  protected JdbcDatabase getDatabase(JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);

    return Databases.createJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        getDriverClass(),
        "allowLoadLocalInfile=true");
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbcUrl.toString());

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new MySQLDestination();
    LOGGER.info("starting destination: {}", MySQLDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MySQLDestination.class);
  }

}
