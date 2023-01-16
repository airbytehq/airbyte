/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bytehouse;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;

import java.util.Collections;
import java.util.Map;
import java.util.function.Consumer;

import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.sql.DataSource;

public class BytehouseDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(BytehouseDestination.class);

  public static final String DRIVER_CLASS = DatabaseDriver.BYTEHOUSE.getDriverClassName();

  public BytehouseDestination() {
    super(DRIVER_CLASS, new BytehouseSQLNameTransformer(), new BytehouseSqlOperations());
  }

  public static void main(String[] args) throws Exception {
    LOGGER.info("starting destination: {}", BytehouseDestination.class);
    new IntegrationRunner(new BytehouseDestination()).run(args);
    LOGGER.info("completed destination: {}", BytehouseDestination.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    // TODO
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final NamingConventionTransformer namingResolver = getNamingResolver();
      final String outputSchema = namingResolver.getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, namingResolver, getSqlOperations());
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
    return Collections.emptyMap();
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    return null;
  }

  @Override
  public AirbyteMessageConsumer getConsumer(JsonNode config, io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog catalog, Consumer<io.airbyte.protocol.models.v0.AirbyteMessage> outputRecordCollector) {
    //TODO
    return null;
  }
}
