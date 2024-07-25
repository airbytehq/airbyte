/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore.initialsync;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.singlestore.SingleStoreSourceOperations;
import io.airbyte.integrations.source.singlestore.SingleStoreType;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreInitialLoadHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreInitialLoadHandler.class);
  private static final long RECORD_LOGGING_SAMPLE_RATE = 1_000_000;
  private static final long DEFAULT_CHUNK_SIZE = 1_000_000;
  private final JsonNode config;
  private final JdbcDatabase database;
  private final SingleStoreSourceOperations sourceOperations;
  private final String quoteString;
  private final SingleStoreInitialLoadStreamStateManager initialLoadStateManager;
  private final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;

  public SingleStoreInitialLoadHandler(final JsonNode config,
                                       final JdbcDatabase database,
                                       final SingleStoreSourceOperations sourceOperations,
                                       final String quoteString,
                                       final SingleStoreInitialLoadStreamStateManager initialLoadStateManager,
                                       final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.config = config;
    this.database = database;
    this.sourceOperations = sourceOperations;
    this.quoteString = quoteString;
    this.initialLoadStateManager = initialLoadStateManager;
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<SingleStoreType>>> tableNameToTable,
                                                                             final Instant emittedAt) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String streamName = stream.getName();
      final String namespace = stream.getNamespace();
      final List<String> primaryKeys = stream.getSourceDefinedPrimaryKey().stream().flatMap(pk -> Stream.of(pk.get(0))).toList();
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(namespace, streamName);
      if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
        LOGGER.info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
        continue;
      }
      if (airbyteStream.getSyncMode().equals(SyncMode.INCREMENTAL)) {
        // Grab the selected fields to sync
        final TableInfo<CommonField<SingleStoreType>> table = tableNameToTable.get(fullyQualifiedTableName);
        final List<String> selectedDatabaseFields = table.getFields().stream().map(CommonField::getName)
            .filter(CatalogHelpers.getTopLevelFieldNames(airbyteStream)::contains).collect(Collectors.toList());

        // This is to handle the case if the user de-selects the PK column
        // Necessary to query the data via pk but won't be added to the final record
        primaryKeys.forEach(pk -> {
          if (!selectedDatabaseFields.contains(pk)) {
            selectedDatabaseFields.add(0, pk);
          }
        });

        final AutoCloseableIterator<JsonNode> queryStream = new SingleStoreInitialLoadRecordIterator(database, sourceOperations, quoteString,
            initialLoadStateManager, selectedDatabaseFields, pair, DEFAULT_CHUNK_SIZE, isCompositePrimaryKey(airbyteStream));
        final AutoCloseableIterator<AirbyteMessage> recordIterator = getRecordIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
        final AutoCloseableIterator<AirbyteMessage> recordAndMessageIterator = augmentWithState(recordIterator, airbyteStream, pair);
        iteratorList.add(augmentWithLogs(recordAndMessageIterator, pair, streamName));
      }
    }
    return iteratorList;
  }

  private static boolean isCompositePrimaryKey(final ConfiguredAirbyteStream stream) {
    return stream.getStream().getSourceDefinedPrimaryKey().size() > 1;
  }

  // Transforms the given iterator to create an {@link AirbyteRecordMessage}
  private AutoCloseableIterator<AirbyteMessage> getRecordIterator(final AutoCloseableIterator<JsonNode> recordIterator,
                                                                  final String streamName,
                                                                  final String namespace,
                                                                  final long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage().withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream(streamName).withNamespace(namespace).withEmittedAt(emittedAt).withData(r)));
  }

  // Augments the given iterator with record count logs.
  private AutoCloseableIterator<AirbyteMessage> augmentWithLogs(final AutoCloseableIterator<AirbyteMessage> iterator,
                                                                final AirbyteStreamNameNamespacePair pair,
                                                                final String streamName) {
    final AtomicLong recordCount = new AtomicLong();
    return AutoCloseableIterators.transform(iterator, AirbyteStreamUtils.convertFromNameAndNamespace(pair.getName(), pair.getNamespace()), r -> {
      final long count = recordCount.incrementAndGet();
      if (count % RECORD_LOGGING_SAMPLE_RATE == 0) {
        LOGGER.info("Reading stream {}. Records read: {}", streamName, count);
      }
      return r;
    });
  }

  private AutoCloseableIterator<AirbyteMessage> augmentWithState(final AutoCloseableIterator<AirbyteMessage> recordIterator,
                                                                 final ConfiguredAirbyteStream airbyteStream,
                                                                 final AirbyteStreamNameNamespacePair pair) {
    final Duration syncCheckpointDuration =
        config.get(SYNC_CHECKPOINT_DURATION_PROPERTY) != null ? Duration.ofSeconds(config.get(SYNC_CHECKPOINT_DURATION_PROPERTY).asLong())
            : DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION;
    final long syncCheckpointRecords = config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY) != null ? config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY).asLong()
        : DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS;
    initialLoadStateManager.setStreamStateForIncrementalRunSupplier(streamStateForIncrementalRunSupplier);
    return AutoCloseableIterators.transformIterator(r -> new SourceStateIterator<>(r, airbyteStream, initialLoadStateManager,
        new StateEmitFrequency(syncCheckpointRecords, syncCheckpointDuration)), recordIterator, pair);
  }

}
