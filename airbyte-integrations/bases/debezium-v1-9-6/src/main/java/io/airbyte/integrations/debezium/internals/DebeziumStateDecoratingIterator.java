/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.debezium.engine.ChangeEvent;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.*;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class encapsulates an iterator and adds the required functionality to create checkpoints for
 * CDC replications. That way, if the process fails in the middle of a long sync, the process is
 * able to recover for any acknowledged checkpoint in the following syncs.
 */
public class DebeziumStateDecoratingIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  public static final Integer SYNC_CHECKPOINT_SECONDS = 15*60;
  public static final Integer SYNC_CHECKPOINT_RECORDS = 10_000;

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumStateDecoratingIterator.class);

  private final Iterator<ChangeEvent<String, String>> changeEventIterator;
  private final CdcStateHandler cdcStateHandler;
  private final AirbyteFileOffsetBackingStore offsetManager;
  private final boolean trackSchemaHistory;
  private final AirbyteSchemaHistoryStorage schemaHistoryManager;
  private final CdcMetadataInjector cdcMetadataInjector;
  private final Instant emittedAt;

  private boolean isSyncFinished;

  /**
   * These parameters control when a checkpoint message has to be sent in a CDC integration. We can
   * emit a checkpoint when any of the following two conditions are met.
   * <p/>
   * 1. The amount of records in the current loop ({@code SYNC_CHECKPOINT_RECORDS}) is higher than a
   * threshold defined by {@code SYNC_CHECKPOINT_RECORDS}.
   * <p/>
   * 2. Time between checkpoints ({@code dateTimeLastSync}) is higher than a {@code Duration} defined
   * at {@code SYNC_CHECKPOINT_SECONDS}.
   * <p/>
   */
  private final Duration syncCheckpointDuration;
  private final Integer syncCheckpointRecords;
  private OffsetDateTime dateTimeLastSync;
  private Integer recordsLastSync;
  private Map<String, String> checkpointOffset;
  private Map<String, String> previousCheckpointOffset;
  private boolean sendCheckpointMessage;

  /**
   * @param changeEventIterator Base iterator that we want to enrich with checkpoint messages
   * @param cdcStateHandler Handler to save the offset and schema history
   * @param offsetManager Handler to read and write debezium offset file
   * @param trackSchemaHistory Set true if the schema needs to be tracked
   * @param schemaHistoryManager Handler to write schema. Needs to be initialized if
   *        trackSchemaHistory is set to true
   * @param checkpointSeconds Seconds between syncs
   * @param checkpointRecords Number of records between syncs
   */
  public DebeziumStateDecoratingIterator(final Iterator<ChangeEvent<String, String>> changeEventIterator,
                                         final CdcStateHandler cdcStateHandler,
                                         final CdcMetadataInjector cdcMetadataInjector,
                                         final Instant emittedAt,
                                         final AirbyteFileOffsetBackingStore offsetManager,
                                         final boolean trackSchemaHistory,
                                         final AirbyteSchemaHistoryStorage schemaHistoryManager,
                                         final Integer checkpointSeconds,
                                         final Integer checkpointRecords) {
    this.changeEventIterator = changeEventIterator;
    this.cdcStateHandler = cdcStateHandler;
    this.cdcMetadataInjector = cdcMetadataInjector;
    this.emittedAt = emittedAt;
    this.offsetManager = offsetManager;
    this.trackSchemaHistory = trackSchemaHistory;
    this.schemaHistoryManager = schemaHistoryManager;

    this.syncCheckpointDuration = Duration.ofSeconds(checkpointSeconds);
    this.syncCheckpointRecords = checkpointRecords;
    this.isSyncFinished = false;
    this.previousCheckpointOffset = new HashMap<>();
    resetCheckpointValues();
  }

  /**
   * Computes the next record retrieved from Source stream. Emits state messages as checkpoints based
   * on number of records or time lapsed.
   *
   * <p>
   * If this method throws an exception, it will propagate outward to the {@code hasNext} or
   * {@code next} invocation that invoked this method. Any further attempts to use the iterator will
   * result in an {@link IllegalStateException}.
   * </p>
   *
   * @return {@link AirbyteStateMessage} containing CDC data or state checkpoint message.
   */
  @Override
  protected AirbyteMessage computeNext() {
    if (isSyncFinished) {
      return endOfData();
    }

    if (sendCheckpointMessage) {
      AirbyteMessage stateMessage = createStateMessage(checkpointOffset);
      previousCheckpointOffset.clear();
      previousCheckpointOffset.putAll(checkpointOffset);
      resetCheckpointValues();
      return stateMessage;
    }

    if (changeEventIterator.hasNext()) {
      try {
        final ChangeEvent<String, String> event = changeEventIterator.next();
        recordsLastSync++;

        if (checkpointOffset == null &&
            (recordsLastSync >= syncCheckpointRecords ||
                Duration.between(dateTimeLastSync, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)) {
          checkpointOffset = offsetManager.read();
          if (!previousCheckpointOffset.isEmpty() &&
              cdcStateHandler.isSameOffset(checkpointOffset, previousCheckpointOffset)){
            checkpointOffset = null;
          }
        }

        if (checkpointOffset != null
            && changeEventIterator.hasNext()
            && !cdcStateHandler.isSnapshotEvent(event)
            && cdcStateHandler.isRecordBehindOffset(checkpointOffset, event)) {
          sendCheckpointMessage = true;
        }

        return DebeziumEventUtils.toAirbyteMessage(event, cdcMetadataInjector, emittedAt);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    }

    isSyncFinished = true;
    return createStateMessage(offsetManager.read());
  }

  /**
   * Initialize or reset the checkpoint variables.
   */
  private void resetCheckpointValues() {
    sendCheckpointMessage = false;
    checkpointOffset = null;
    recordsLastSync = 0;
    dateTimeLastSync = OffsetDateTime.now();
  }

  /**
   * Creates {@link AirbyteStateMessage} while updating CDC data, used to checkpoint the state of the
   * process.
   *
   * @return {@link AirbyteStateMessage} which includes offset and schema history if used.
   */
  private AirbyteMessage createStateMessage(Map<String, String> offset) {
    if (trackSchemaHistory && schemaHistoryManager == null) {
      throw new RuntimeException("Schema History Tracking is true but manager is not initialised");
    }
    if (offsetManager == null) {
      throw new RuntimeException("Offset can not be null");
    }

    return cdcStateHandler.saveState(offset, schemaHistoryManager != null ? schemaHistoryManager.read() : null);
  }

}
