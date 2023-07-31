/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeDestinationResolver.getNumberOfFileBuffers;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoopTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import io.airbyte.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Collections;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeInternalStagingDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeInternalStagingDestination.class);
  private final String airbyteEnvironment;

  public SnowflakeInternalStagingDestination(final String airbyteEnvironment) {
    this(new SnowflakeSQLNameTransformer(), airbyteEnvironment);
  }

  public SnowflakeInternalStagingDestination(final NamingConventionTransformer nameTransformer, final String airbyteEnvironment) {
    super("", nameTransformer, new SnowflakeInternalStagingSqlOperations(nameTransformer));
    this.airbyteEnvironment = airbyteEnvironment;
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    final NamingConventionTransformer nameTransformer = getNamingResolver();
    final SnowflakeInternalStagingSqlOperations snowflakeInternalStagingSqlOperations = new SnowflakeInternalStagingSqlOperations(nameTransformer);
    final DataSource dataSource = getDataSource(config);
    try {
      final JdbcDatabase database = getDatabase(dataSource);
      final String outputSchema = nameTransformer.getIdentifier(config.get("schema").asText());
      attemptTableOperations(outputSchema, database, nameTransformer,
          snowflakeInternalStagingSqlOperations, true);
      attemptStageOperations(outputSchema, database, nameTransformer, snowflakeInternalStagingSqlOperations);
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

  private static void attemptStageOperations(final String outputSchema,
                                             final JdbcDatabase database,
                                             final NamingConventionTransformer namingResolver,
                                             final SnowflakeInternalStagingSqlOperations sqlOperations)
      throws Exception {

    // verify we have permissions to create/drop stage
    final String outputTableName = namingResolver.getIdentifier("_airbyte_connection_test_" + UUID.randomUUID().toString().replaceAll("-", ""));
    final String stageName = sqlOperations.getStageName(outputSchema, outputTableName);
    sqlOperations.createStageIfNotExists(database, stageName);

    // try to make test write to make sure we have required role
    try {
      sqlOperations.attemptWriteToStage(outputSchema, stageName, database);
    } finally {
      // drop created tmp stage
      sqlOperations.dropStageIfExists(database, stageName);
    }
  }

  @Override
  protected DataSource getDataSource(final JsonNode config) {
    return SnowflakeDatabase.createDataSource(config, airbyteEnvironment);
  }

  @Override
  protected JdbcDatabase getDatabase(final DataSource dataSource) {
    return SnowflakeDatabase.getDatabase(dataSource);
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return Collections.emptyMap();
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
    SnowflakeSqlGenerator sqlGenerator = new SnowflakeSqlGenerator();
    ParsedCatalog parsedCatalog = new CatalogParser(sqlGenerator).parseCatalog(catalog);
    TyperDeduper typerDeduper;
    if (TypingAndDedupingFlag.isDestinationV2()) {
      typerDeduper = new DefaultTyperDeduper<>(sqlGenerator, new SnowflakeDestinationHandler(getDatabase(getDataSource(config))), parsedCatalog);
    } else {
      typerDeduper = new NoopTyperDeduper();
    }

    return new StagingConsumerFactory().create(
        outputRecordCollector,
        getDatabase(getDataSource(config)),
        new SnowflakeInternalStagingSqlOperations(getNamingResolver()),
        getNamingResolver(),
        CsvSerializedBuffer.createFunction(null, () -> new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX, getNumberOfFileBuffers(config))),
        config,
        catalog,
        true,
        new TypeAndDedupeOperationValve(),
        typerDeduper,
        parsedCatalog);
  }

  @Override
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final Consumer<AirbyteMessage> outputRecordCollector) {
    SnowflakeSqlGenerator sqlGenerator = new SnowflakeSqlGenerator();
    ParsedCatalog parsedCatalog = new CatalogParser(sqlGenerator).parseCatalog(catalog);
    TyperDeduper typerDeduper;
    if (TypingAndDedupingFlag.isDestinationV2()) {
      typerDeduper = new DefaultTyperDeduper<>(sqlGenerator, new SnowflakeDestinationHandler(getDatabase(getDataSource(config))), parsedCatalog);
    } else {
      typerDeduper = new NoopTyperDeduper();
    }

    return new StagingConsumerFactory().createAsync(
        outputRecordCollector,
        getDatabase(getDataSource(config)),
        new SnowflakeInternalStagingSqlOperations(getNamingResolver()),
        getNamingResolver(),
        config,
        catalog,
        true,
        new TypeAndDedupeOperationValve(),
        typerDeduper,
        parsedCatalog);
  }

}
