/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV2TableMigrator;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeInternalStagingDestination extends AbstractJdbcDestination implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeInternalStagingDestination.class);
  public static final String RAW_SCHEMA_OVERRIDE = "raw_data_schema";

  public static final String DISABLE_TYPE_DEDUPE = "disable_type_dedupe";
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
  public SerializedAirbyteMessageConsumer getSerializedMessageConsumer(final JsonNode config,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final Consumer<AirbyteMessage> outputRecordCollector) {
    final String defaultNamespace = config.get("schema").asText();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      if (StringUtils.isEmpty(stream.getStream().getNamespace())) {
        stream.getStream().setNamespace(defaultNamespace);
      }
    }

    final SnowflakeSqlGenerator sqlGenerator = new SnowflakeSqlGenerator();
    final ParsedCatalog parsedCatalog;
    final TyperDeduper typerDeduper;
    final JdbcDatabase database = getDatabase(getDataSource(config));
    final String databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    final SnowflakeDestinationHandler snowflakeDestinationHandler = new SnowflakeDestinationHandler(databaseName, database);
    final CatalogParser catalogParser;
    if (TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent()) {
      catalogParser = new CatalogParser(sqlGenerator, TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get());
    } else {
      catalogParser = new CatalogParser(sqlGenerator);
    }
    parsedCatalog = catalogParser.parseCatalog(catalog);
    final SnowflakeV1V2Migrator migrator = new SnowflakeV1V2Migrator(getNamingResolver(), database, databaseName);
    final SnowflakeV2TableMigrator v2TableMigrator = new SnowflakeV2TableMigrator(database, databaseName, sqlGenerator, snowflakeDestinationHandler);
    boolean disableTypeDedupe = config.has(DISABLE_TYPE_DEDUPE) && config.get(DISABLE_TYPE_DEDUPE).asBoolean(false);
    final int defaultThreadCount = 8;
    if (disableTypeDedupe) {
      typerDeduper = new NoOpTyperDeduperWithV1V2Migrations<>(sqlGenerator, snowflakeDestinationHandler, parsedCatalog, migrator, v2TableMigrator,
          defaultThreadCount);
    } else {
      typerDeduper =
          new DefaultTyperDeduper<>(sqlGenerator, snowflakeDestinationHandler, parsedCatalog, migrator, v2TableMigrator, defaultThreadCount);
    }

    return new StagingConsumerFactory().createAsync(
        outputRecordCollector,
        database,
        new SnowflakeInternalStagingSqlOperations(getNamingResolver()),
        getNamingResolver(),
        config,
        catalog,
        true,
        new TypeAndDedupeOperationValve(),
        typerDeduper,
        parsedCatalog,
        defaultNamespace,
        true,
        Optional.of(getSnowflakeBufferMemoryLimit()));
  }

  private static long getSnowflakeBufferMemoryLimit() {
    return (long) (Runtime.getRuntime().maxMemory() * 0.5);
  }

}
