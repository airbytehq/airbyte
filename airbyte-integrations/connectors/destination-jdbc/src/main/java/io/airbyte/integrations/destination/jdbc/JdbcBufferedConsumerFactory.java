/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.NamingHelper;
import io.airbyte.integrations.destination.WriteConfig;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer.OnStartFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer.RecordWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.SyncMode;
import java.util.List;
import java.util.Map;
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

  public static DestinationConsumer<AirbyteMessage> create(JdbcDatabase database,
                                                           SqlOperations sqlOperations,
                                                           NamingConventionTransformer namingResolver,
                                                           JsonNode config,
                                                           ConfiguredAirbyteCatalog catalog) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog);

    return new BufferedStreamConsumer(
        onStartFunction(database, sqlOperations, writeConfigs),
        recordWriterFunction(database, sqlOperations, writeConfigs, catalog),
        onCloseFunction(database, sqlOperations, writeConfigs),
        catalog,
        writeConfigs.stream().map(WriteConfig::getStreamName).collect(Collectors.toSet()));
  }

  private static List<WriteConfig> createWriteConfigs(NamingConventionTransformer namingResolver, JsonNode config, ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream().map(stream -> {
      final String streamName = stream.getStream().getName();
      final String schemaName = namingResolver.getIdentifier(stream.getTargetNamespace());
      final String tableName = namingResolver.getIdentifier(stream.getAliasName());
      final String tmpSchemaName = NamingHelper.getTmpSchemaName(namingResolver, schemaName);
      final String tmpTableName = NamingHelper.getTmpTableName(namingResolver, tableName);
      final SyncMode syncMode = stream.getSyncMode() != null ? stream.getSyncMode() : SyncMode.FULL_REFRESH;
      return new WriteConfig(streamName, tmpSchemaName, tmpTableName, tableName, syncMode);
    }).collect(Collectors.toList());
  }

  private static OnStartFunction onStartFunction(JdbcDatabase database, SqlOperations sqlOperations, List<WriteConfig> writeConfigs) {
    return () -> {
      LOGGER.info("Preparing tmp tables in destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String tmpSchemaName = writeConfig.getTmpNamespaceName();
        final String tmpTableName = writeConfig.getTmpTableName();
        LOGGER.info("Preparing tmp table in destination started for stream {}. schema {}, tmp table name: {}", writeConfig.getStreamName(),
            tmpSchemaName, tmpTableName);

        sqlOperations.createSchemaIfNotExists(database, tmpSchemaName);
        sqlOperations.createTableIfNotExists(database, tmpSchemaName, tmpTableName);
      }
      LOGGER.info("Preparing tables in destination completed.");
    };
  }

  private static RecordWriter recordWriterFunction(JdbcDatabase database,
                                                   SqlOperations sqlOperations,
                                                   List<WriteConfig> writeConfigs,
                                                   ConfiguredAirbyteCatalog catalog) {
    final Map<String, WriteConfig> streamNameToWriteConfig = writeConfigs.stream()
        .collect(Collectors.toUnmodifiableMap(WriteConfig::getStreamName, Function.identity()));

    return (streamName, recordStream) -> {
      if (!streamNameToWriteConfig.containsKey(streamName)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
      }

      final WriteConfig writeConfig = streamNameToWriteConfig.get(streamName);
      sqlOperations.insertRecords(database, recordStream, writeConfig.getTmpNamespaceName(), writeConfig.getTmpTableName());
    };
  }

  private static OnCloseFunction onCloseFunction(JdbcDatabase database, SqlOperations sqlOperations, List<WriteConfig> writeConfigs) {
    return (hasFailed) -> {
      // copy data
      if (!hasFailed) {
        final StringBuilder queries = new StringBuilder();
        LOGGER.info("Finalizing tables in destination started for {} streams", writeConfigs.size());
        for (WriteConfig writeConfig : writeConfigs) {
          final String tmpSchemaName = writeConfig.getTmpNamespaceName();
          final String srcTableName = writeConfig.getTmpTableName();
          final String dstTableName = writeConfig.getOutputTableName();
          LOGGER.info("Finalizing stream {}. schema {}, tmp table {}, final table {}",
              writeConfig.getStreamName(), tmpSchemaName, srcTableName, dstTableName);

          sqlOperations.createTableIfNotExists(database, tmpSchemaName, dstTableName);
          switch (writeConfig.getSyncMode()) {
            case FULL_REFRESH -> queries.append(sqlOperations.truncateTableQuery(tmpSchemaName, dstTableName));
            case INCREMENTAL -> {}
            default -> throw new IllegalStateException("Unrecognized sync mode: " + writeConfig.getSyncMode());
          }
          queries.append(sqlOperations.copyTableQuery(tmpSchemaName, srcTableName, dstTableName));
        }

        LOGGER.info("Executing finalization of tables.");
        sqlOperations.executeTransaction(database, queries.toString());
        LOGGER.info("Finalizing tables in destination completed.");
      }
      // clean up
      LOGGER.info("Cleaning tmp tables in destination started for {} streams", writeConfigs.size());
      for (WriteConfig writeConfig : writeConfigs) {
        final String tmpSchemaName = writeConfig.getTmpNamespaceName();
        final String tmpTableName = writeConfig.getTmpTableName();
        LOGGER.info("Cleaning tmp table in destination started for stream {}. schema {}, tmp table name: {}", writeConfig.getStreamName(),
            tmpSchemaName,
            tmpTableName);

        sqlOperations.dropTableIfExists(database, tmpSchemaName, tmpTableName);
      }
      LOGGER.info("Cleaning tmp tables in destination completed.");
    };
  }

}
