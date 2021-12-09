/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Snowflake Internal Staging consists of 4 main parts
 *
 * CREATE STAGE @TEMP_STAGE_NAME -- Creates a new named internal stage to use for loading data from
 * files into Snowflake tables and unloading data from tables into files PUT
 * file://local/<file-patterns> @TEMP_STAGE_NAME. --JDBC Driver will upload the files into stage
 * COPY FROM @TEMP_STAGE_NAME -- Loads data from staged files to an existing table.
 * DROP @TEMP_STAGE_NAME -- Drop temporary stage after sync
 */
public class SnowflakeInternalStagingConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeInternalStagingConsumerFactory.class);

  private static final long MAX_BATCH_SIZE_BYTES = 1024 * 1024 * 1024 / 4; // 256mb

  public static AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
                                              final JdbcDatabase database,
                                              final SnowflakeStagingSqlOperations sqlOperations,
                                              final SnowflakeSQLNameTransformer namingResolver,
                                              final JsonNode config,
                                              final ConfiguredAirbyteCatalog catalog) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog);

    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(database, sqlOperations, writeConfigs, namingResolver),
        recordWriterFunction(database, sqlOperations, writeConfigs, catalog, namingResolver),
        onCloseFunction(database, sqlOperations, writeConfigs, namingResolver),
        catalog,
        sqlOperations::isValidData,
        MAX_BATCH_SIZE_BYTES);
  }

  private static List<WriteConfig> createWriteConfigs(final NamingConventionTransformer namingResolver,
                                                      final JsonNode config,
                                                      final ConfiguredAirbyteCatalog catalog) {

    return catalog.getStreams().stream().map(toWriteConfig(namingResolver, config)).collect(Collectors.toList());
  }

  private static Function<ConfiguredAirbyteStream, WriteConfig> toWriteConfig(
                                                                              final NamingConventionTransformer namingResolver,
                                                                              final JsonNode config) {
    return stream -> {
      Preconditions.checkNotNull(stream.getDestinationSyncMode(), "Undefined destination sync mode");
      final AirbyteStream abStream = stream.getStream();

      final String outputSchema = getOutputSchema(abStream, namingResolver.getIdentifier(config.get("schema").asText()));

      final String streamName = abStream.getName();
      final String tableName = namingResolver.getRawTableName(streamName);
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();

      final WriteConfig writeConfig = new WriteConfig(streamName, abStream.getNamespace(), outputSchema, tmpTableName, tableName, syncMode);
      LOGGER.info("Write config: {}", writeConfig);

      return writeConfig;
    };
  }

  private static String getOutputSchema(final AirbyteStream stream, final String defaultDestSchema) {
    final String sourceSchema = stream.getNamespace();
    if (sourceSchema != null) {
      return sourceSchema;
    }
    return defaultDestSchema;
  }

  private static OnStartFunction onStartFunction(final JdbcDatabase database,
                                                 final SnowflakeStagingSqlOperations snowflakeSqlOperations,
                                                 final List<WriteConfig> writeConfigs,
                                                 final SnowflakeSQLNameTransformer namingResolver) {
    return () -> {
      LOGGER.info("Preparing tmp tables in destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schemaName = writeConfig.getOutputSchemaName();
        final String tmpTableName = writeConfig.getTmpTableName();
        LOGGER.info("Preparing tmp table in destination started for stream {}. schema: {}, tmp table name: {}", writeConfig.getStreamName(),
            schemaName, tmpTableName);
        final String outputTableName = writeConfig.getOutputTableName();
        final String stageName = namingResolver.getStageName(schemaName, outputTableName);
        LOGGER.info("Preparing stage in destination started for stream {}. schema: {}, stage: {}", writeConfig.getStreamName(),
            schemaName, stageName);

        snowflakeSqlOperations.createSchemaIfNotExists(database, schemaName);
        snowflakeSqlOperations.createTableIfNotExists(database, schemaName, tmpTableName);
        snowflakeSqlOperations.createStageIfNotExists(database, stageName);
        LOGGER.info("Preparing stages in destination completed " + stageName);

      }
      LOGGER.info("Preparing tables in destination completed.");
    };
  }

  private static AirbyteStreamNameNamespacePair toNameNamespacePair(final WriteConfig config) {
    return new AirbyteStreamNameNamespacePair(config.getStreamName(), config.getNamespace());
  }

  private static RecordWriter recordWriterFunction(final JdbcDatabase database,
                                                   final SqlOperations snowflakeSqlOperations,
                                                   final List<WriteConfig> writeConfigs,
                                                   final ConfiguredAirbyteCatalog catalog,
                                                   final SnowflakeSQLNameTransformer namingResolver) {
    final Map<AirbyteStreamNameNamespacePair, WriteConfig> pairToWriteConfig =
        writeConfigs.stream()
            .collect(Collectors.toUnmodifiableMap(
                SnowflakeInternalStagingConsumerFactory::toNameNamespacePair, Function.identity()));

    return (pair, records) -> {
      if (!pairToWriteConfig.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
      }

      final WriteConfig writeConfig = pairToWriteConfig.get(pair);
      final String schemaName = writeConfig.getOutputSchemaName();
      final String tableName = writeConfig.getOutputTableName();
      final String stageName = namingResolver.getStageName(schemaName, tableName);

      snowflakeSqlOperations.insertRecords(database, records, schemaName, stageName);
    };
  }

  private static OnCloseFunction onCloseFunction(final JdbcDatabase database,
                                                 final SnowflakeStagingSqlOperations sqlOperations,
                                                 final List<WriteConfig> writeConfigs,
                                                 final SnowflakeSQLNameTransformer namingResolver) {
    return (hasFailed) -> {
      if (!hasFailed) {
        final List<String> queryList = new ArrayList<>();
        LOGGER.info("Finalizing tables in destination started for {} streams", writeConfigs.size());
        for (final WriteConfig writeConfig : writeConfigs) {
          final String schemaName = writeConfig.getOutputSchemaName();
          final String srcTableName = writeConfig.getTmpTableName();
          final String dstTableName = writeConfig.getOutputTableName();
          LOGGER.info("Finalizing stream {}. schema {}, tmp table {}, final table {}", writeConfig.getStreamName(), schemaName, srcTableName,
              dstTableName);

          final String stageName = namingResolver.getStageName(schemaName, dstTableName);
          sqlOperations.copyIntoTmpTableFromStage(database, stageName, srcTableName, schemaName);
          LOGGER.info("Uploading data from stage:  stream {}. schema {}, tmp table {}, stage {}", writeConfig.getStreamName(), schemaName,
              srcTableName,
              stageName);
          sqlOperations.createTableIfNotExists(database, schemaName, dstTableName);
          switch (writeConfig.getSyncMode()) {
            case OVERWRITE -> queryList.add(sqlOperations.truncateTableQuery(database, schemaName, dstTableName));
            case APPEND, APPEND_DEDUP -> {}
            default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
          }
          queryList.add(sqlOperations.copyTableQuery(database, schemaName, srcTableName, dstTableName));
        }

        LOGGER.info("Executing finalization of tables.");
        sqlOperations.executeTransaction(database, queryList);
        LOGGER.info("Finalizing tables in destination completed.");
      }
      LOGGER.info("Cleaning tmp tables in destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schemaName = writeConfig.getOutputSchemaName();
        final String tmpTableName = writeConfig.getTmpTableName();
        LOGGER.info("Cleaning tmp table in destination started for stream {}. schema {}, tmp table name: {}", writeConfig.getStreamName(), schemaName,
            tmpTableName);

        sqlOperations.dropTableIfExists(database, schemaName, tmpTableName);
        final String outputTableName = writeConfig.getOutputTableName();
        final String stageName = namingResolver.getStageName(schemaName, outputTableName);
        LOGGER.info("Cleaning stage in destination started for stream {}. schema {}, stage: {}", writeConfig.getStreamName(), schemaName,
            stageName);
        sqlOperations.dropStageIfExists(database, stageName);
      }
      LOGGER.info("Cleaning tmp tables and stages in destination completed.");
    };
  }

}
