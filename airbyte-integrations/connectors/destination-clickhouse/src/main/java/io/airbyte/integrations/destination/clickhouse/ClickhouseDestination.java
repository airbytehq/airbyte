/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseDestination.class);

  public static final String DRIVER_CLASS = "ru.yandex.clickhouse.ClickHouseDriver";

  public ClickhouseDestination() {
    super(DRIVER_CLASS, new ClickhouseSQLNameTransformer(), new ClickhouseSqlOperations());
  }

  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    final List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:clickhouse://%s:%s/%s",
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

  public static void main(String[] args) throws Exception {
    final Destination destination = new ClickhouseDestination();
    LOGGER.info("starting destination: {}", ClickhouseDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", ClickhouseDestination.class);
  }

}
