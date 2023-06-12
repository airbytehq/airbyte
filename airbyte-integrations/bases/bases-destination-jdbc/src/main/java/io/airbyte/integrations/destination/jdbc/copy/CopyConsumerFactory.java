/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy;

import static io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES;

import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.CheckAndRemoveRecordWriter;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.record_buffer.InMemoryRecordBufferingStrategy;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CopyConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(CopyConsumerFactory.class);

  public static <T> AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
                                                  final DataSource dataSource,
                                                  final JdbcDatabase database,
                                                  final SqlOperations sqlOperations,
                                                  final StandardNameTransformer namingResolver,
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

    // TODO: (ryankfu) remove this once we have a better way to handle this
    final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount = new HashMap<>();
    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(pairToIgnoredRecordCount),
        new InMemoryRecordBufferingStrategy(
            recordWriterFunction(pairToCopier, sqlOperations, pairToIgnoredRecordCount),
            removeStagingFilePrinter(pairToCopier),
            DEFAULT_MAX_BATCH_SIZE_BYTES),
        onCloseFunction(pairToCopier, database, sqlOperations, pairToIgnoredRecordCount, dataSource),
        catalog,
        sqlOperations::isValidData);
  }

  private static <T> Map<AirbyteStreamNameNamespacePair, StreamCopier> createWriteConfigs(final StandardNameTransformer namingResolver,
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
      final var pair = AirbyteStreamNameNamespacePair.fromAirbyteStream(stream);
      final var copier = streamCopierFactory.create(defaultSchema, config, stagingFolder, configuredStream, namingResolver, database, sqlOperations);

      pairToCopier.put(pair, copier);
    }

    return pairToCopier;
  }

  private static OnStartFunction onStartFunction(final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount) {
    return pairToIgnoredRecordCount::clear;
  }

  private static RecordWriter<AirbyteRecordMessage> recordWriterFunction(final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier,
                                                                         final SqlOperations sqlOperations,
                                                                         final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount) {
    return (final AirbyteStreamNameNamespacePair pair, final List<AirbyteRecordMessage> records) -> {
      final var fileName = pairToCopier.get(pair).prepareStagingFile();
      for (final AirbyteRecordMessage recordMessage : records) {
        final var id = UUID.randomUUID();
        // 1s1t provides a framework in which we can handle this record (i.e. alerting via the airbyte_meta column)
        pairToCopier.get(pair).write(id, recordMessage, fileName);
      }
    };
  }

  private static CheckAndRemoveRecordWriter removeStagingFilePrinter(final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier) {
    return (final AirbyteStreamNameNamespacePair pair, final String stagingFileName) -> {
      final String currentFileName = pairToCopier.get(pair).getCurrentFile();
      if (stagingFileName != null && currentFileName != null && !stagingFileName.equals(currentFileName)) {
        pairToCopier.get(pair).closeNonCurrentStagingFileWriters();
      }
      return currentFileName;
    };
  }

  private static OnCloseFunction onCloseFunction(final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier,
                                                 final JdbcDatabase database,
                                                 final SqlOperations sqlOperations,
                                                 final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount,
                                                 final DataSource dataSource) {
    return (hasFailed) -> {
      closeAsOneTransaction(pairToCopier, hasFailed, database, sqlOperations, dataSource);
    };
  }

  private static void closeAsOneTransaction(final Map<AirbyteStreamNameNamespacePair, StreamCopier> pairToCopier,
                                            boolean hasFailed,
                                            final JdbcDatabase db,
                                            final SqlOperations sqlOperations,
                                            final DataSource dataSource)
      throws Exception {
    Exception firstException = null;
    final List<StreamCopier> streamCopiers = new ArrayList<>(pairToCopier.values());
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

      DataSourceFactory.close(dataSource);
    }
    if (firstException != null) {
      throw firstException;
    }
  }

}
