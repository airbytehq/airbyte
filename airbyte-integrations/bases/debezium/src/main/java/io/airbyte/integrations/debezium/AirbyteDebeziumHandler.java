/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.debezium.internals.*;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.engine.ChangeEvent;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.Properties;
import java.util.concurrent.LinkedBlockingQueue;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class acts as the bridge between Airbyte DB connectors and debezium. If a DB connector wants
 * to use debezium for CDC, it should use this class
 */
public class AirbyteDebeziumHandler<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteDebeziumHandler.class);
  /**
   * We use 10000 as capacity cause the default queue size and batch size of debezium is :
   * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_BATCH_SIZE}is 2048
   * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_QUEUE_SIZE} is 8192
   */
  private static final int QUEUE_CAPACITY = 10000;

  private final JsonNode config;
  private final CdcTargetPosition<T> targetPosition;
  private final boolean trackSchemaHistory;
  private final Duration firstRecordWaitTime;

  public AirbyteDebeziumHandler(final JsonNode config,
                                final CdcTargetPosition<T> targetPosition,
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

    final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator<>(
        queue,
        targetPosition,
        tableSnapshotPublisher::hasClosed,
        new DebeziumShutdownProcedure<>(queue, tableSnapshotPublisher::close, tableSnapshotPublisher::hasClosed),
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
                                                                       final Instant emittedAt,
                                                                       final boolean addDbNameToState) {
    LOGGER.info("Using CDC: {}", true);
    final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>(QUEUE_CAPACITY);
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(cdcSavedInfoFetcher.getSavedOffset(),
        addDbNameToState ? Optional.ofNullable(config.get(JdbcUtils.DATABASE_KEY).asText()) : Optional.empty());
    final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager = schemaHistoryManager(cdcSavedInfoFetcher);
    final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(connectorProperties, config, catalog, offsetManager,
        schemaHistoryManager);
    publisher.start(queue);

    // handle state machine around pub/sub logic.
    final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator<>(
        queue,
        targetPosition,
        publisher::hasClosed,
        new DebeziumShutdownProcedure<>(queue, publisher::close, publisher::hasClosed),
        firstRecordWaitTime);

    final Duration syncCheckpointDuration =
        config.get("sync_checkpoint_seconds") != null ? Duration.ofSeconds(config.get("sync_checkpoint_seconds").asLong())
            : DebeziumStateDecoratingIterator.SYNC_CHECKPOINT_DURATION;
    final Long syncCheckpointRecords = config.get("sync_checkpoint_records") != null ? config.get("sync_checkpoint_records").asLong()
        : DebeziumStateDecoratingIterator.SYNC_CHECKPOINT_RECORDS;
    return AutoCloseableIterators.fromIterator(new DebeziumStateDecoratingIterator<>(
        eventIterator,
        cdcStateHandler,
        targetPosition,
        cdcMetadataInjector,
        emittedAt,
        offsetManager,
        trackSchemaHistory,
        schemaHistoryManager.orElse(null),
        syncCheckpointDuration,
        syncCheckpointRecords));
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
