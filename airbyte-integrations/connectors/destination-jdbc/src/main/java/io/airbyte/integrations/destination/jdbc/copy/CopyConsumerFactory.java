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

package io.airbyte.integrations.destination.jdbc.copy;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CopyConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(CopyConsumerFactory.class);

  private static final int MAX_BATCH_SIZE = 10000;

  public static <T> AirbyteMessageConsumer create(Consumer<AirbyteMessage> outputRecordCollector,
                                                  JdbcDatabase database,
                                                  SqlOperations sqlOperations,
                                                  ExtendedNameTransformer namingResolver,
                                                  T config,
                                                  ConfiguredAirbyteCatalog catalog,
                                                  StreamCopierFactory<T> streamCopierFactory,
                                                  String defaultSchema) {
    final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier = createWriteConfigs(
        namingResolver,
        config,
        catalog,
        streamCopierFactory,
        defaultSchema,
        database,
        sqlOperations);

    final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount = new HashMap<>();
    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(pairToIgnoredRecordCount),
        recordWriterFunction(pairToCopier, sqlOperations, pairToIgnoredRecordCount),
        onCloseFunction(pairToCopier, database, sqlOperations, pairToIgnoredRecordCount),
        catalog,
        sqlOperations::isValidData,
        MAX_BATCH_SIZE);
  }

  private static <T> Map<AirbyteStreamNameNamespacePair, StreamCopier> createWriteConfigs(ExtendedNameTransformer namingResolver,
                                                                                          T config,
                                                                                          ConfiguredAirbyteCatalog catalog,
                                                                                          StreamCopierFactory<T> streamCopierFactory,
                                                                                          String defaultSchema,
                                                                                          JdbcDatabase database,
                                                                                          SqlOperations sqlOperations) {
    Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier = new HashMap<>();
    final String stagingFolder = UUID.randomUUID().toString();
    for (var configuredStream : catalog.getStreams()) {
      var stream = configuredStream.getStream();
      var pair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream);
      var syncMode = configuredStream.getDestinationSyncMode();
      var copier = streamCopierFactory.create(defaultSchema, config, stagingFolder, syncMode, stream, namingResolver, database, sqlOperations);

      pairToCopier.put(pair, copier);
    }

    return pairToCopier;
  }

  private static OnStartFunction onStartFunction(Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount) {
    return pairToIgnoredRecordCount::clear;
  }

  private static RecordWriter recordWriterFunction(Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier,
                                                   SqlOperations sqlOperations,
                                                   Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount) {
    return (AirbyteStreamNameNamespacePair pair, List<AirbyteRecordMessage> records) -> {
      for (AirbyteRecordMessage recordMessage : records) {
        var id = UUID.randomUUID();
        if (sqlOperations.isValidData(recordMessage.getData())) {
          // TODO Truncate json data instead of throwing whole record away?
          // or should we upload it into a special rejected record folder in s3 instead?
          var emittedAt = Timestamp.from(Instant.ofEpochMilli(recordMessage.getEmittedAt()));
          pairToCopier.get(pair).write(id, Jsons.serialize(recordMessage.getData()), emittedAt);
        } else {
          pairToIgnoredRecordCount.put(pair, pairToIgnoredRecordCount.getOrDefault(pair, 0L) + 1L);
        }
      }
    };
  }

  private static OnCloseFunction onCloseFunction(Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier,
                                                 JdbcDatabase database,
                                                 SqlOperations sqlOperations,
                                                 Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount) {
    return (hasFailed) -> {
      pairToIgnoredRecordCount
          .forEach((pair, count) -> LOGGER.warn("A total of {} record(s) of data from stream {} were invalid and were ignored.", count, pair));
      closeAsOneTransaction(new ArrayList<>(pairToCopier.values()), hasFailed, database, sqlOperations);
    };
  }

  private static void closeAsOneTransaction(List<StreamCopier> streamCopiers, boolean hasFailed, JdbcDatabase db, SqlOperations sqlOperations)
      throws Exception {
    Exception firstException = null;
    try {
      List<String> queries = new ArrayList<>();
      for (var copier : streamCopiers) {
        try {
          copier.closeStagingUploader(hasFailed);

          if (!hasFailed) {
            copier.createDestinationSchema();
            copier.createTemporaryTable();
            copier.copyStagingFileToTemporaryTable();
            var destTableName = copier.createDestinationTable();
            var mergeQuery = copier.generateMergeStatement(destTableName);
            queries.add(mergeQuery);
          }
        } catch (Exception e) {
          final String message = String.format("Failed to finalize copy to temp table due to: %s", e);
          LOGGER.error(message);
          hasFailed = true;
          if (firstException == null) {
            firstException = e;
          }
        }
      }
      if (!hasFailed) {
        sqlOperations.executeTransaction(db, queries);
      }
    } finally {
      for (var copier : streamCopiers) {
        copier.removeFileAndDropTmpTable();
      }
    }
    if (firstException != null) {
      throw firstException;
    }
  }

}
