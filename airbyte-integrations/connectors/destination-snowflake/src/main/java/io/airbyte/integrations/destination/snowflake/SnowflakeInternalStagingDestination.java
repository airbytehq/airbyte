/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.JavaBaseConstants.DestinationColumns;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.AbstractJdbcDestination;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.destination.staging.StagingConsumerFactory;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.DefaultTyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.NoOpTyperDeduperWithV1V2Migrations;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV1V2Migrator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeV2TableMigrator;
import io.airbyte.integrations.destination.snowflake.typing_deduping.migrations.SnowflakeState;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeInternalStagingDestination extends AbstractJdbcDestination<SnowflakeState> implements Destination {

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
      sqlOperations.dropStageIfExists(database, stageName, null);
    }
  }

  @Override
  public DataSource getDataSource(final JsonNode config) {
    return SnowflakeDatabase.createDataSource(config, airbyteEnvironment);
  }

  @Override
  public JdbcDatabase getDatabase(final DataSource dataSource) {
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
  protected JdbcSqlGenerator getSqlGenerator(final JsonNode config) {
    throw new UnsupportedOperationException("Snowflake does not yet use the native JDBC DV2 interface");
  }

  @Override
  protected JdbcDestinationHandler<SnowflakeState> getDestinationHandler(String databaseName, JdbcDatabase database, String rawTableSchema) {
    throw new UnsupportedOperationException("Snowflake does not yet use the native JDBC DV2 interface");
  }

  @Override
  protected List<Migration<SnowflakeState>> getMigrations(JdbcDatabase database,
                                                          String databaseName,
                                                          SqlGenerator sqlGenerator,
                                                          DestinationHandler<SnowflakeState> destinationHandler) {
    return List.of();
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

    final int retentionPeriodDays = SnowflakeSqlOperations.getRetentionPeriodDays(
        config.get(SnowflakeSqlOperations.RETENTION_PERIOD_DAYS_CONFIG_KEY));

    final SnowflakeSqlGenerator sqlGenerator = new SnowflakeSqlGenerator(retentionPeriodDays);
    final ParsedCatalog parsedCatalog;
    final TyperDeduper typerDeduper;
    final JdbcDatabase database = getDatabase(getDataSource(config));
    final String databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    final String rawTableSchemaName;
    final CatalogParser catalogParser;
    if (TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).isPresent()) {
      rawTableSchemaName = TypingAndDedupingFlag.getRawNamespaceOverride(RAW_SCHEMA_OVERRIDE).get();
      catalogParser = new CatalogParser(sqlGenerator, rawTableSchemaName);
    } else {
      rawTableSchemaName = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
      catalogParser = new CatalogParser(sqlGenerator);
    }
    final SnowflakeDestinationHandler snowflakeDestinationHandler = new SnowflakeDestinationHandler(databaseName, database, rawTableSchemaName);
    parsedCatalog = catalogParser.parseCatalog(catalog);
    final SnowflakeV1V2Migrator migrator = new SnowflakeV1V2Migrator(getNamingResolver(), database, databaseName);
    final SnowflakeV2TableMigrator v2TableMigrator = new SnowflakeV2TableMigrator(database, databaseName, sqlGenerator, snowflakeDestinationHandler);
    final boolean disableTypeDedupe = config.has(DISABLE_TYPE_DEDUPE) && config.get(DISABLE_TYPE_DEDUPE).asBoolean(false);
    final List<Migration<SnowflakeState>> migrations = getMigrations(database, databaseName, sqlGenerator, snowflakeDestinationHandler);
    if (disableTypeDedupe) {
      typerDeduper =
          new NoOpTyperDeduperWithV1V2Migrations<>(sqlGenerator, snowflakeDestinationHandler, parsedCatalog, migrator, v2TableMigrator, migrations);
    } else {
      typerDeduper =
          new DefaultTyperDeduper<>(
              sqlGenerator,
              snowflakeDestinationHandler,
              parsedCatalog,
              migrator,
              v2TableMigrator,
              migrations);
    }

    return StagingConsumerFactory.builder(
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
        DestinationColumns.V2_WITHOUT_META)
        .setBufferMemoryLimit(Optional.of(getSnowflakeBufferMemoryLimit()))
        .setOptimalBatchSizeBytes(
            // The per stream size limit is following recommendations from:
            // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
            // "To optimize the number of parallel operations for a load,
            // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size compressed."
            200 * 1024 * 1024)
        .build()
        .createAsync();
  }

  private static long getSnowflakeBufferMemoryLimit() {
    return (long) (Runtime.getRuntime().maxMemory() * 0.5);
  }

}
