/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.integrations.debezium.internals.DebeziumEventUtils;
import io.airbyte.integrations.debezium.internals.DebeziumRecordIterator;
import io.airbyte.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.engine.ChangeEvent;
import java.time.Duration;
import java.time.Instant;
import java.util.Iterator;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class acts as the bridge between Airbyte DB connectors and debezium. If a DB connector wants
 * to use debezium for CDC, it should use this class
 */
public class AirbyteDebeziumHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteDebeziumHandler.class);
  /**
   * We use 10000 as capacity cause the default queue size and batch size of debezium is :
   * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_BATCH_SIZE}is 2048
   * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_QUEUE_SIZE} is 8192
   */
  private static final int QUEUE_CAPACITY = 10000;

  private final JsonNode config;
  private final CdcTargetPosition targetPosition;
  private final boolean trackSchemaHistory;
  private final Duration firstRecordWaitTime;

  public AirbyteDebeziumHandler(final JsonNode config,
                                final CdcTargetPosition targetPosition,
                                final boolean trackSchemaHistory,
                                final Duration firstRecordWaitTime) {
    this.config = config;
    this.targetPosition = targetPosition;
    this.trackSchemaHistory = trackSchemaHistory;
    this.firstRecordWaitTime = firstRecordWaitTime;
  }

  public AutoCloseableIterator<AirbyteMessage> getSnapshotIterators(
                                                                    final ConfiguredAirbyteCatalog catalogContainingStreamsToSnapshot,
                                                                    final CdcMetadataInjector cdcMetadataInjector,
                                                                    final Properties snapshotProperties,
                                                                    final CdcStateHandler cdcStateHandler,
                                                                    final Instant emittedAt) {

    LOGGER.info("Running snapshot for " + catalogContainingStreamsToSnapshot.getStreams().size() + " new tables");
    final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>(QUEUE_CAPACITY);

    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeDummyStateForSnapshotPurpose();
    final DebeziumRecordPublisher tableSnapshotPublisher = new DebeziumRecordPublisher(snapshotProperties,
        config,
        catalogContainingStreamsToSnapshot,
        offsetManager,
        schemaHistoryManager(new EmptySavedInfo()));
    tableSnapshotPublisher.start(queue);

    final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator(
        queue,
        targetPosition,
        tableSnapshotPublisher::hasClosed,
        tableSnapshotPublisher::close,
        firstRecordWaitTime);

    return AutoCloseableIterators.concatWithEagerClose(AutoCloseableIterators
        .transform(
            eventIterator,
            (event) -> DebeziumEventUtils.toAirbyteMessage(event, cdcMetadataInjector, emittedAt)),
        AutoCloseableIterators
            .fromIterator(MoreIterators.singletonIteratorFromSupplier(cdcStateHandler::saveStateAfterCompletionOfSnapshotOfNewStreams)));
  }

  public AutoCloseableIterator<AirbyteMessage> getIncrementalIterators(final ConfiguredAirbyteCatalog catalog,
                                                                       final CdcSavedInfoFetcher cdcSavedInfoFetcher,
                                                                       final CdcStateHandler cdcStateHandler,
                                                                       final CdcMetadataInjector cdcMetadataInjector,
                                                                       final Properties connectorProperties,
                                                                       final Instant emittedAt) {
    LOGGER.info("Using CDC: {}", true);
    final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>(QUEUE_CAPACITY);
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(cdcSavedInfoFetcher.getSavedOffset());
    final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager = schemaHistoryManager(cdcSavedInfoFetcher);
    final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(connectorProperties, config, catalog, offsetManager,
        schemaHistoryManager);
    publisher.start(queue);

    // handle state machine around pub/sub logic.
    final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator(
        queue,
        targetPosition,
        publisher::hasClosed,
        publisher::close,
        firstRecordWaitTime);

    // convert to airbyte message.
    final AutoCloseableIterator<AirbyteMessage> messageIterator = AutoCloseableIterators
        .transform(
            eventIterator,
            (event) -> DebeziumEventUtils.toAirbyteMessage(event, cdcMetadataInjector, emittedAt));

    // our goal is to get the state at the time this supplier is called (i.e. after all message records
    // have been produced)
    final Supplier<AirbyteMessage> stateMessageSupplier = () -> {
      final Map<String, String> offset = offsetManager.read();
      final String dbHistory = trackSchemaHistory ? schemaHistoryManager
          .orElseThrow(() -> new RuntimeException("Schema History Tracking is true but manager is not initialised")).read() : null;

      return cdcStateHandler.saveState(offset, dbHistory);
    };

    // wrap the supplier in an iterator so that we can concat it to the message iterator.
    final Iterator<AirbyteMessage> stateMessageIterator = MoreIterators.singletonIteratorFromSupplier(stateMessageSupplier);

    // this structure guarantees that the debezium engine will be closed, before we attempt to emit the
    // state file. we want this so that we have a guarantee that the debezium offset file (which we use
    // to produce the state file) is up-to-date.

    return AutoCloseableIterators.concatWithEagerClose(messageIterator, AutoCloseableIterators.fromIterator(stateMessageIterator));
  }

  private Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager(final CdcSavedInfoFetcher cdcSavedInfoFetcher) {
    if (trackSchemaHistory) {
      return Optional.of(AirbyteSchemaHistoryStorage.initializeDBHistory(cdcSavedInfoFetcher.getSavedSchemaHistory()));
    }

    return Optional.empty();
  }

  public static boolean shouldUseCDC(final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode)
        .anyMatch(syncMode -> syncMode == SyncMode.INCREMENTAL);
  }

  private static class EmptySavedInfo implements CdcSavedInfoFetcher {

    @Override
    public JsonNode getSavedOffset() {
      return null;
    }

    @Override
    public Optional<JsonNode> getSavedSchemaHistory() {
      return Optional.empty();
    }

  }

}
