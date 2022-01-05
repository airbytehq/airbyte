/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeInternalStagingDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeInternalStagingDestination.class);

  public SnowflakeInternalStagingDestination() {
    super("", new SnowflakeSQLNameTransformer(), new SnowflakeStagingSqlOperations());
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    SnowflakeSQLNameTransformer nameTransformer = new SnowflakeSQLNameTransformer();
    SnowflakeStagingSqlOperations snowflakeStagingSqlOperations = new SnowflakeStagingSqlOperations();
    try (final JdbcDatabase database = getDatabase(config)) {
      final String outputSchema = super.getNamingResolver().getIdentifier(config.get("schema").asText());
      attemptSQLCreateAndDropTableOperations(outputSchema, database, nameTransformer, snowflakeStagingSqlOperations);
      attemptSQLCreateAndDropStages(outputSchema, database, nameTransformer, snowflakeStagingSqlOperations);
      return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED)
          .withMessage("Could not connect with provided configuration. \n" + e.getMessage());
    }
  }

  private static void attemptSQLCreateAndDropStages(String outputSchema,
                                                    JdbcDatabase database,
                                                    SnowflakeSQLNameTransformer namingResolver,
                                                    SnowflakeStagingSqlOperations sqlOperations)
      throws Exception {

    // verify we have permissions to create/drop stage
    final String outputTableName = namingResolver.getIdentifier("_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", ""));
    String stageName = namingResolver.getStageName(outputSchema, outputTableName);;
    sqlOperations.createStageIfNotExists(database, stageName);
    sqlOperations.dropStageIfExists(database, stageName);
  }

  @Override
  protected JdbcDatabase getDatabase(final JsonNode config) {
    return SnowflakeDatabase.getDatabase(config);
  }

  // this is a no op since we override getDatabase.
  @Override
  public JsonNode toJdbcConfig(final JsonNode config) {
    return Jsons.emptyObject();
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    return SnowflakeInternalStagingConsumerFactory.create(outputRecordCollector, getDatabase(config),
        new SnowflakeStagingSqlOperations(), new SnowflakeSQLNameTransformer(), config, catalog);
  }

}
