/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

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
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// Strategy:
// 1. Create a temporary table for each stream
// 2. Accumulate records in a buffer. One buffer per stream.
// 3. As records accumulate write them in batch to the database. We set a minimum numbers of records
// before writing to avoid wasteful record-wise writes.
// 4. Once all records have been written to buffer, flush the buffer and write any remaining records
// to the database (regardless of how few are left).
// 5. In a single transaction, delete the target tables if they exist and rename the temp tables to
// the final table name.
public class JdbcBufferedConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcBufferedConsumerFactory.class);

  private static final int MAX_BATCH_SIZE = 10000;

  public static AirbyteMessageConsumer create(Consumer<AirbyteMessage> outputRecordCollector,
                                              JdbcDatabase database,
                                              SqlOperations sqlOperations,
                                              NamingConventionTransformer namingResolver,
                                              JsonNode config,
                                              ConfiguredAirbyteCatalog catalog) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog, sqlOperations.isSchemaRequired());

    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(database, sqlOperations, writeConfigs),
        recordWriterFunction(database, sqlOperations, writeConfigs, catalog),
        onCloseFunction(database, sqlOperations, writeConfigs),
        catalog,
        sqlOperations::isValidData,
        MAX_BATCH_SIZE);
  }

  private static List<WriteConfig> createWriteConfigs(NamingConventionTransformer namingResolver,
                                                      JsonNode config,
                                                      ConfiguredAirbyteCatalog catalog,
                                                      boolean schemaRequired) {
    if (schemaRequired) {
      Preconditions.checkState(config.has("schema"), "jdbc destinations must specify a schema.");
    }
    final Instant now = Instant.now();
    return catalog.getStreams().stream().map(toWriteConfig(namingResolver, config, now, schemaRequired)).collect(Collectors.toList());
  }

  private static Function<ConfiguredAirbyteStream, WriteConfig> toWriteConfig(
                                                                              NamingConventionTransformer namingResolver,
                                                                              JsonNode config,
                                                                              Instant now,
                                                                              boolean schemaRequired) {
    return stream -> {
      Preconditions.checkNotNull(stream.getDestinationSyncMode(), "Undefined destination sync mode");
      final AirbyteStream abStream = stream.getStream();

      final String defaultSchemaName = schemaRequired ? namingResolver.getIdentifier(config.get("schema").asText())
          : namingResolver.getIdentifier(config.get("database").asText());
      final String outputSchema = getOutputSchema(abStream, defaultSchemaName);

      final String streamName = abStream.getName();
      final String tableName = namingResolver.getRawTableName(streamName);
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();

      final WriteConfig writeConfig = new WriteConfig(streamName, abStream.getNamespace(), outputSchema, tmpTableName, tableName, syncMode);
      LOGGER.info("Write config: {}", writeConfig);

      return writeConfig;
    };
  }

  /**
   * Defer to the {@link AirbyteStream}'s namespace. If this is not set, use the destination's default
   * schema. This namespace is source-provided, and can be potentially empty.
   *
   * The logic here matches the logic in the catalog_process.py for Normalization. Any modifications
   * need to be reflected there and vice versa.
   */
  private static String getOutputSchema(AirbyteStream stream, String defaultDestSchema) {
    final String sourceSchema = stream.getNamespace();
    if (sourceSchema != null) {
      return sourceSchema;
    }
    return defaultDestSchema;
  }

  private static OnStartFunction onStartFunction(JdbcDatabase database, SqlOperations sqlOperations, List<WriteConfig> writeConfigs) {
    return () -> {
      LOGGER.info("Preparing tmp tables in destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schemaName = writeConfig.getOutputSchemaName();
        final String tmpTableName = writeConfig.getTmpTableName();
        LOGGER.info("Preparing tmp table in destination started for stream {}. schema: {}, tmp table name: {}", writeConfig.getStreamName(),
            schemaName, tmpTableName);

        sqlOperations.createSchemaIfNotExists(database, schemaName);
        sqlOperations.createTableIfNotExists(database, schemaName, tmpTableName);
      }
      LOGGER.info("Preparing tables in destination completed.");
    };
  }

  private static RecordWriter recordWriterFunction(JdbcDatabase database,
                                                   SqlOperations sqlOperations,
                                                   List<WriteConfig> writeConfigs,
                                                   ConfiguredAirbyteCatalog catalog) {
    final Map<AirbyteStreamNameNamespacePair, WriteConfig> pairToWriteConfig = writeConfigs.stream()
        .collect(Collectors.toUnmodifiableMap(JdbcBufferedConsumerFactory::toNameNamespacePair, Function.identity()));

    return (pair, records) -> {
      if (!pairToWriteConfig.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
      }

      final WriteConfig writeConfig = pairToWriteConfig.get(pair);
      sqlOperations.insertRecords(database, records, writeConfig.getOutputSchemaName(), writeConfig.getTmpTableName());
    };
  }

  private static OnCloseFunction onCloseFunction(JdbcDatabase database, SqlOperations sqlOperations, List<WriteConfig> writeConfigs) {
    return (hasFailed) -> {
      // copy data
      if (!hasFailed) {
        List<String> queryList = new ArrayList<>();
        LOGGER.info("Finalizing tables in destination started for {} streams", writeConfigs.size());
        for (WriteConfig writeConfig : writeConfigs) {
          final String schemaName = writeConfig.getOutputSchemaName();
          final String srcTableName = writeConfig.getTmpTableName();
          final String dstTableName = writeConfig.getOutputTableName();
          LOGGER.info("Finalizing stream {}. schema {}, tmp table {}, final table {}", writeConfig.getStreamName(), schemaName, srcTableName,
              dstTableName);

          sqlOperations.createTableIfNotExists(database, schemaName, dstTableName);
          switch (writeConfig.getSyncMode()) {
            case OVERWRITE -> queryList.add(sqlOperations.truncateTableQuery(database, schemaName, dstTableName));
            case APPEND -> {}
            case APPEND_DEDUP -> {}
            default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
          }
          queryList.add(sqlOperations.copyTableQuery(database, schemaName, srcTableName, dstTableName));
        }

        LOGGER.info("Executing finalization of tables.");
        sqlOperations.executeTransaction(database, queryList);
        LOGGER.info("Finalizing tables in destination completed.");
      }
      // clean up
      LOGGER.info("Cleaning tmp tables in destination started for {} streams", writeConfigs.size());
      for (WriteConfig writeConfig : writeConfigs) {
        final String schemaName = writeConfig.getOutputSchemaName();
        final String tmpTableName = writeConfig.getTmpTableName();
        LOGGER.info("Cleaning tmp table in destination started for stream {}. schema {}, tmp table name: {}", writeConfig.getStreamName(), schemaName,
            tmpTableName);

        sqlOperations.dropTableIfExists(database, schemaName, tmpTableName);
      }
      LOGGER.info("Cleaning tmp tables in destination completed.");
    };
  }

  private static AirbyteStreamNameNamespacePair toNameNamespacePair(WriteConfig config) {
    return new AirbyteStreamNameNamespacePair(config.getStreamName(), config.getNamespace());
  }

}
