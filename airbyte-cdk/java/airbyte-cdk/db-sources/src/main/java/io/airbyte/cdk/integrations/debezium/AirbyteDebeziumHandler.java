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
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordIterator;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumShutdownProcedure;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumStateDecoratingIterator;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import java.time.Duration;
import java.util.Optional;
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
  public static final int QUEUE_CAPACITY = 10_000;

  private final JsonNode config;
  private final CdcTargetPosition<T> targetPosition;
  private final boolean trackSchemaHistory;
  private final Duration firstRecordWaitTime, subsequentRecordWaitTime;
  private final int queueSize;
  private final boolean addDbNameToOffsetState;

  public AirbyteDebeziumHandler(final JsonNode config,
                                final CdcTargetPosition<T> targetPosition,
                                final boolean trackSchemaHistory,
                                final Duration firstRecordWaitTime,
                                final Duration subsequentRecordWaitTime,
                                final int queueSize,
                                final boolean addDbNameToOffsetState) {
    this.config = config;
    this.targetPosition = targetPosition;
    this.trackSchemaHistory = trackSchemaHistory;
    this.firstRecordWaitTime = firstRecordWaitTime;
    this.subsequentRecordWaitTime = subsequentRecordWaitTime;
    this.queueSize = queueSize;
    this.addDbNameToOffsetState = addDbNameToOffsetState;
  }

  public AutoCloseableIterator<AirbyteMessage> getIncrementalIterators(final DebeziumPropertiesManager debeziumPropertiesManager,
                                                                       final DebeziumEventConverter eventConverter,
                                                                       final CdcSavedInfoFetcher cdcSavedInfoFetcher,
                                                                       final CdcStateHandler cdcStateHandler) {
    LOGGER.info("Using CDC: {}", true);
    LOGGER.info("Using DBZ version: {}", DebeziumEngine.class.getPackage().getImplementationVersion());
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(
        cdcSavedInfoFetcher.getSavedOffset(),
        addDbNameToOffsetState ? Optional.ofNullable(config.get(JdbcUtils.DATABASE_KEY).asText()) : Optional.empty());
    final var schemaHistoryManager = trackSchemaHistory
        ? Optional.of(AirbyteSchemaHistoryStorage.initializeDBHistory(
            cdcSavedInfoFetcher.getSavedSchemaHistory(), cdcStateHandler.compressSchemaHistoryForState()))
        : Optional.<AirbyteSchemaHistoryStorage>empty();
    final var publisher = new DebeziumRecordPublisher(debeziumPropertiesManager);
    final var queue = new LinkedBlockingQueue<ChangeEvent<String, String>>(queueSize);
    publisher.start(queue, offsetManager, schemaHistoryManager);
    // handle state machine around pub/sub logic.
    final AutoCloseableIterator<ChangeEventWithMetadata> eventIterator = new DebeziumRecordIterator<>(
        queue,
        targetPosition,
        publisher::hasClosed,
        new DebeziumShutdownProcedure<>(queue, publisher::close, publisher::hasClosed),
        firstRecordWaitTime,
        subsequentRecordWaitTime);

    final Duration syncCheckpointDuration = config.has(SYNC_CHECKPOINT_DURATION_PROPERTY)
        ? Duration.ofSeconds(config.get(SYNC_CHECKPOINT_DURATION_PROPERTY).asLong())
        : SYNC_CHECKPOINT_DURATION;
    final Long syncCheckpointRecords = config.has(SYNC_CHECKPOINT_RECORDS_PROPERTY)
        ? config.get(SYNC_CHECKPOINT_RECORDS_PROPERTY).asLong()
        : SYNC_CHECKPOINT_RECORDS;
    return AutoCloseableIterators.fromIterator(new DebeziumStateDecoratingIterator<>(
        eventIterator,
        cdcStateHandler,
        targetPosition,
        eventConverter,
        offsetManager,
        trackSchemaHistory,
        schemaHistoryManager.orElse(null),
        syncCheckpointDuration,
        syncCheckpointRecords));
  }

  public static boolean isAnyStreamIncrementalSyncMode(final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode)
        .anyMatch(syncMode -> syncMode == SyncMode.INCREMENTAL);
  }

}
