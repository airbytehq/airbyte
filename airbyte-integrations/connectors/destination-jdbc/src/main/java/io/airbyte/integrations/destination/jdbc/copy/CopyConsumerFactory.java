/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy;

import static io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES;

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

  public static <T> AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
                                                  final JdbcDatabase database,
                                                  final SqlOperations sqlOperations,
                                                  final ExtendedNameTransformer namingResolver,
                                                  final T config,
                                                  final ConfiguredAirbyteCatalog catalog,
                                                  final StreamCopierFactory<T> streamCopierFactory,
                                                  final String defaultSchema) {
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
        DEFAULT_MAX_BATCH_SIZE_BYTES);
  }

  private static <T> Map<AirbyteStreamNameNamespacePair, StreamCopier> createWriteConfigs(final ExtendedNameTransformer namingResolver,
                                                                                          final T config,
                                                                                          final ConfiguredAirbyteCatalog catalog,
                                                                                          final StreamCopierFactory<T> streamCopierFactory,
                                                                                          final String defaultSchema,
                                                                                          final JdbcDatabase database,
                                                                                          final SqlOperations sqlOperations) {
    final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier = new HashMap<>();
    final String stagingFolder = UUID.randomUUID().toString();
    for (final var configuredStream : catalog.getStreams()) {
      final var stream = configuredStream.getStream();
      final var pair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream);
      final var copier = streamCopierFactory.create(defaultSchema, config, stagingFolder, configuredStream, namingResolver, database, sqlOperations);

      pairToCopier.put(pair, copier);
    }

    return pairToCopier;
  }

  private static OnStartFunction onStartFunction(final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount) {
    return pairToIgnoredRecordCount::clear;
  }

  private static RecordWriter recordWriterFunction(final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier,
                                                   final SqlOperations sqlOperations,
                                                   final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount) {
    return (AirbyteStreamNameNamespacePair pair, List<AirbyteRecordMessage> records) -> {
      final var fileName = pairToCopier.get(pair).prepareStagingFile();
      for (final AirbyteRecordMessage recordMessage : records) {
        final var id = UUID.randomUUID();
        if (sqlOperations.isValidData(recordMessage.getData())) {
          // TODO Truncate json data instead of throwing whole record away?
          // or should we upload it into a special rejected record folder in s3 instead?
          pairToCopier.get(pair).write(id, recordMessage, fileName);
        } else {
          pairToIgnoredRecordCount.put(pair, pairToIgnoredRecordCount.getOrDefault(pair, 0L) + 1L);
        }
      }
    };
  }

  private static OnCloseFunction onCloseFunction(final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier,
                                                 final JdbcDatabase database,
                                                 final SqlOperations sqlOperations,
                                                 final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount) {
    return (hasFailed) -> {
      pairToIgnoredRecordCount
          .forEach((pair, count) -> LOGGER.warn("A total of {} record(s) of data from stream {} were invalid and were ignored.", count, pair));
      closeAsOneTransaction(new ArrayList<>(pairToCopier.values()), hasFailed, database, sqlOperations);
    };
  }

  private static void closeAsOneTransaction(final List<StreamCopier> streamCopiers,
                                            boolean hasFailed,
                                            final JdbcDatabase db,
                                            final SqlOperations sqlOperations)
      throws Exception {
    Exception firstException = null;
    try {
      final List<String> queries = new ArrayList<>();
      for (final var copier : streamCopiers) {
        try {
          copier.closeStagingUploader(hasFailed);

          if (!hasFailed) {
            copier.createDestinationSchema();
            copier.createTemporaryTable();
            copier.copyStagingFileToTemporaryTable();
            final var destTableName = copier.createDestinationTable();
            final var mergeQuery = copier.generateMergeStatement(destTableName);
            queries.add(mergeQuery);
          }
        } catch (final Exception e) {
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
      for (final var copier : streamCopiers) {
        copier.removeFileAndDropTmpTable();
      }
    }
    if (firstException != null) {
      throw firstException;
    }
  }

}
