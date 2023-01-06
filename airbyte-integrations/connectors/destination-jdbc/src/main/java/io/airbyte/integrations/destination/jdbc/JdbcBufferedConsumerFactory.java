/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import static io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.integrations.destination.record_buffer.InMemoryRecordBufferingStrategy;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
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

  public static AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
                                              final JdbcDatabase database,
                                              final SqlOperations sqlOperations,
                                              final NamingConventionTransformer namingResolver,
                                              final JsonNode config,
                                              final ConfiguredAirbyteCatalog catalog) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog, sqlOperations.isSchemaRequired());

    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(database, sqlOperations, writeConfigs),
        new InMemoryRecordBufferingStrategy(recordWriterFunction(database, sqlOperations, writeConfigs, catalog), DEFAULT_MAX_BATCH_SIZE_BYTES),
        onCloseFunction(database, sqlOperations, writeConfigs),
        catalog,
        sqlOperations::isValidData);
  }

  private static List<WriteConfig> createWriteConfigs(final NamingConventionTransformer namingResolver,
                                                      final JsonNode config,
                                                      final ConfiguredAirbyteCatalog catalog,
                                                      final boolean schemaRequired) {
    if (schemaRequired) {
      Preconditions.checkState(config.has("schema"), "jdbc destinations must specify a schema.");
    }
    final Instant now = Instant.now();
    return catalog.getStreams().stream().map(toWriteConfig(namingResolver, config, now, schemaRequired)).collect(Collectors.toList());
  }

  private static Function<ConfiguredAirbyteStream, WriteConfig> toWriteConfig(
                                                                              final NamingConventionTransformer namingResolver,
                                                                              final JsonNode config,
                                                                              final Instant now,
                                                                              final boolean schemaRequired) {
    return stream -> {
      Preconditions.checkNotNull(stream.getDestinationSyncMode(), "Undefined destination sync mode");
      final AirbyteStream abStream = stream.getStream();

      final String defaultSchemaName = schemaRequired ? namingResolver.getIdentifier(config.get("schema").asText())
          : namingResolver.getIdentifier(config.get(JdbcUtils.DATABASE_KEY).asText());
      final String outputSchema = getOutputSchema(abStream, defaultSchemaName, namingResolver);

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
   * <p>
   * The logic here matches the logic in the catalog_process.py for Normalization. Any modifications
   * need to be reflected there and vice versa.
   */
  private static String getOutputSchema(final AirbyteStream stream,
                                        final String defaultDestSchema,
                                        final NamingConventionTransformer namingResolver) {
    return stream.getNamespace() != null
        ? namingResolver.getNamespace(stream.getNamespace())
        : namingResolver.getNamespace(defaultDestSchema);
  }

  private static OnStartFunction onStartFunction(final JdbcDatabase database,
                                                 final SqlOperations sqlOperations,
                                                 final List<WriteConfig> writeConfigs) {
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

  private static RecordWriter<AirbyteRecordMessage> recordWriterFunction(final JdbcDatabase database,
                                                                         final SqlOperations sqlOperations,
                                                                         final List<WriteConfig> writeConfigs,
                                                                         final ConfiguredAirbyteCatalog catalog) {
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

  private static OnCloseFunction onCloseFunction(final JdbcDatabase database,
                                                 final SqlOperations sqlOperations,
                                                 final List<WriteConfig> writeConfigs) {
    return (hasFailed) -> {
      // copy data
      if (!hasFailed) {
        final List<String> queryList = new ArrayList<>();
        sqlOperations.onDestinationCloseOperations(database, writeConfigs);
        LOGGER.info("Finalizing tables in destination started for {} streams", writeConfigs.size());
        for (final WriteConfig writeConfig : writeConfigs) {
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
          queryList.add(sqlOperations.insertTableQuery(database, schemaName, srcTableName, dstTableName));
        }

        LOGGER.info("Executing finalization of tables.");
        sqlOperations.executeTransaction(database, queryList);
        LOGGER.info("Finalizing tables in destination completed.");
      }
      // clean up
      LOGGER.info("Cleaning tmp tables in destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String schemaName = writeConfig.getOutputSchemaName();
        final String tmpTableName = writeConfig.getTmpTableName();
        LOGGER.info("Cleaning tmp table in destination started for stream {}. schema {}, tmp table name: {}", writeConfig.getStreamName(), schemaName,
            tmpTableName);

        sqlOperations.dropTableIfExists(database, schemaName, tmpTableName);
      }
      LOGGER.info("Cleaning tmp tables in destination completed.");
    }

    ;
  }

  private static AirbyteStreamNameNamespacePair toNameNamespacePair(final WriteConfig config) {
    return new AirbyteStreamNameNamespacePair(config.getStreamName(), config.getNamespace());
  }

}
