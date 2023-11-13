/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS;
import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage.SchemaHistory;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumEventUtils;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordIterator;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumShutdownProcedure;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumStateDecoratingIterator;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import java.util.Optional;
import java.util.OptionalInt;
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
  private final OptionalInt queueSize;

  public AirbyteDebeziumHandler(final JsonNode config,
                                final CdcTargetPosition<T> targetPosition,
                                final boolean trackSchemaHistory,
                                final Duration firstRecordWaitTime,
                                final OptionalInt queueSize) {
    this.config = config;
    this.targetPosition = targetPosition;
    this.trackSchemaHistory = trackSchemaHistory;
    this.firstRecordWaitTime = firstRecordWaitTime;
    this.queueSize = queueSize;
  }

  public AutoCloseableIterator<AirbyteMessage> getSnapshotIterators(
                                                                    final ConfiguredAirbyteCatalog catalogContainingStreamsToSnapshot,
                                                                    final CdcMetadataInjector cdcMetadataInjector,
                                                                    final Properties snapshotProperties,
                                                                    final CdcStateHandler cdcStateHandler,
                                                                    final DebeziumPropertiesManager.DebeziumConnectorType debeziumConnectorType,
                                                                    final Instant emittedAt) {

    LOGGER.info("Running snapshot for " + catalogContainingStreamsToSnapshot.getStreams().size() + " new tables");
    final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>(queueSize.orElse(QUEUE_CAPACITY));

    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeDummyStateForSnapshotPurpose();
    final DebeziumRecordPublisher tableSnapshotPublisher = new DebeziumRecordPublisher(snapshotProperties,
        config,
        catalogContainingStreamsToSnapshot,
        offsetManager,
        schemaHistoryManager(new SchemaHistory<>(Optional.empty(), false), cdcStateHandler.compressSchemaHistoryForState()),
        debeziumConnectorType);
    tableSnapshotPublisher.start(queue);

    final AutoCloseableIterator<ChangeEventWithMetadata> eventIterator = new DebeziumRecordIterator<>(
        queue,
        targetPosition,
        tableSnapshotPublisher::hasClosed,
        new DebeziumShutdownProcedure<>(queue, tableSnapshotPublisher::close, tableSnapshotPublisher::hasClosed),
        firstRecordWaitTime);

    return AutoCloseableIterators.concatWithEagerClose(AutoCloseableIterators
        .transform(
            eventIterator,
            (event) -> DebeziumEventUtils.toAirbyteMessage(event, cdcMetadataInjector, catalogContainingStreamsToSnapshot, emittedAt,
                debeziumConnectorType)),
        AutoCloseableIterators
            .fromIterator(MoreIterators.singletonIteratorFromSupplier(cdcStateHandler::saveStateAfterCompletionOfSnapshotOfNewStreams)));
  }

  /**
   * In the default case here, we don't know for sure whether the Debezium Engine will produce records
   * or not. We therefore pass {@link canShortCircuitDebeziumEngine} = false.
   */
  public AutoCloseableIterator<AirbyteMessage> getIncrementalIterators(final ConfiguredAirbyteCatalog catalog,
                                                                       final CdcSavedInfoFetcher cdcSavedInfoFetcher,
                                                                       final CdcStateHandler cdcStateHandler,
                                                                       final CdcMetadataInjector cdcMetadataInjector,
                                                                       final Properties connectorProperties,
                                                                       final DebeziumPropertiesManager.DebeziumConnectorType debeziumConnectorType,
                                                                       final Instant emittedAt,
                                                                       final boolean addDbNameToState) {
    return getIncrementalIterators(
        catalog,
        cdcSavedInfoFetcher,
        cdcStateHandler,
        cdcMetadataInjector,
        connectorProperties,
        debeziumConnectorType,
        emittedAt, addDbNameToState,
        false);
  }

  /**
   *
   * @param canShortCircuitDebeziumEngine This argument may be set to true in cases where we already
   *        know that the Debezium Engine is not going to be producing any change events. In this
   *        case, this method skips provisioning a Debezium Engine altogether.
   */
  public AutoCloseableIterator<AirbyteMessage> getIncrementalIterators(final ConfiguredAirbyteCatalog catalog,
                                                                       final CdcSavedInfoFetcher cdcSavedInfoFetcher,
                                                                       final CdcStateHandler cdcStateHandler,
                                                                       final CdcMetadataInjector cdcMetadataInjector,
                                                                       final Properties connectorProperties,
                                                                       final DebeziumPropertiesManager.DebeziumConnectorType debeziumConnectorType,
                                                                       final Instant emittedAt,
                                                                       final boolean addDbNameToState,
                                                                       final boolean canShortCircuitDebeziumEngine) {
    LOGGER.info("Using CDC: {}", true);
    LOGGER.info("Using DBZ version: {}", DebeziumEngine.class.getPackage().getImplementationVersion());
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(
        cdcSavedInfoFetcher.getSavedOffset(),
        addDbNameToState ? Optional.ofNullable(config.get(JdbcUtils.DATABASE_KEY).asText()) : Optional.empty());
    final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager =
        trackSchemaHistory ? schemaHistoryManager(
            cdcSavedInfoFetcher.getSavedSchemaHistory(),
            cdcStateHandler.compressSchemaHistoryForState())
            : Optional.empty();

    final AutoCloseableIterator<ChangeEventWithMetadata> eventIterator;
    if (!canShortCircuitDebeziumEngine) {
      final var publisher = new DebeziumRecordPublisher(
          connectorProperties, config, catalog, offsetManager, schemaHistoryManager, debeziumConnectorType);
      final var queue = new LinkedBlockingQueue<ChangeEvent<String, String>>(queueSize.orElse(QUEUE_CAPACITY));
      publisher.start(queue);
      // handle state machine around pub/sub logic.
      eventIterator = new DebeziumRecordIterator<>(
          queue,
          targetPosition,
          publisher::hasClosed,
          new DebeziumShutdownProcedure<>(queue, publisher::close, publisher::hasClosed),
          firstRecordWaitTime);
    } else {
      LOGGER.info("Short-circuiting Debezium Engine: nothing of interest in target replication stream interval.");
      eventIterator = AutoCloseableIterators.fromIterator(Collections.emptyIterator());
    }

    final Duration syncCheckpointDuration =
        config.get(SYNC_CHECKPOINT_DURATION_PROPERTY) != null ? Duration.ofSeconds(config.get(SYNC_CHECKPOINT_DURATION_PROPERTY).asLong())
            : SYNC_CHECKPOINT_DURATION;
    final Long syncCheckpointRecords = config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY) != null ? config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY).asLong()
        : SYNC_CHECKPOINT_RECORDS;
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
        syncCheckpointRecords,
        catalog,
        debeziumConnectorType));
  }

  private Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager(final SchemaHistory<Optional<JsonNode>> schemaHistory,
                                                                     final boolean compressSchemaHistoryForState) {
    if (trackSchemaHistory) {
      return Optional.of(AirbyteSchemaHistoryStorage.initializeDBHistory(schemaHistory, compressSchemaHistoryForState));
    }

    return Optional.empty();
  }

  public static boolean isAnyStreamIncrementalSyncMode(final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode)
        .anyMatch(syncMode -> syncMode == SyncMode.INCREMENTAL);
  }

}
