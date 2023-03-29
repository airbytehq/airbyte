/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.google.common.collect.AbstractIterator;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.integrations.debezium.CdcTargetPosition;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.debezium.engine.ChangeEvent;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import org.apache.kafka.connect.errors.ConnectException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class encapsulates CDC change events and adds the required functionality to create
 * checkpoints for CDC replications. That way, if the process fails in the middle of a long sync, it
 * will be able to recover for any acknowledged checkpoint in the next syncs.
 */
public class DebeziumStateDecoratingIterator<T> extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  public static final Duration SYNC_CHECKPOINT_DURATION = Duration.ofMinutes(15);
  public static final Integer SYNC_CHECKPOINT_RECORDS = 10_000;

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumStateDecoratingIterator.class);

  private final Iterator<ChangeEvent<String, String>> changeEventIterator;
  private final CdcStateHandler cdcStateHandler;
  private final CdcTargetPosition<T> targetPosition;
  private final AirbyteFileOffsetBackingStore offsetManager;
  private final boolean trackSchemaHistory;
  private final AirbyteSchemaHistoryStorage schemaHistoryManager;
  private final CdcMetadataInjector cdcMetadataInjector;
  private final Instant emittedAt;

  private boolean isSyncFinished = false;

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
  private final Long syncCheckpointRecords;
  private OffsetDateTime dateTimeLastSync;
  private Long recordsLastSync;
  private boolean sendCheckpointMessage = false;

  /**
   * `checkpointOffsetToSend` is used as temporal storage for the offset that we want to send as
   * message. As Debezium is reading records faster that we process them, if we try to send
   * `offsetManger.read()` offset, it is possible that the state is behind the record we are currently
   * propagating. To avoid that, we store the offset as soon as we reach the checkpoint threshold
   * (time or records) and we wait to send it until we are sure that the record we are processing is
   * behind the offset to be sent.
   */
  private final HashMap<String, String> checkpointOffsetToSend = new HashMap<>();

  /**
   * `previousCheckpointOffset` is used to make sure we don't send duplicated states with the same
   * offset. Is it possible that the offset Debezium report doesn't move for a period of time, and if
   * we just rely on the `offsetManger.read()`, there is a chance to sent duplicate states, generating
   * an unneeded usage of networking and processing.
   */
  private final HashMap<String, String> previousCheckpointOffset;

  /**
   * @param changeEventIterator Base iterator that we want to enrich with checkpoint messages
   * @param cdcStateHandler Handler to save the offset and schema history
   * @param offsetManager Handler to read and write debezium offset file
   * @param trackSchemaHistory Set true if the schema needs to be tracked
   * @param schemaHistoryManager Handler to write schema. Needs to be initialized if
   *        trackSchemaHistory is set to true
   * @param checkpointDuration Duration object with time between syncs
   * @param checkpointRecords Number of records between syncs
   */
  public DebeziumStateDecoratingIterator(final Iterator<ChangeEvent<String, String>> changeEventIterator,
                                         final CdcStateHandler cdcStateHandler,
                                         final CdcTargetPosition<T> targetPosition,
                                         final CdcMetadataInjector cdcMetadataInjector,
                                         final Instant emittedAt,
                                         final AirbyteFileOffsetBackingStore offsetManager,
                                         final boolean trackSchemaHistory,
                                         final AirbyteSchemaHistoryStorage schemaHistoryManager,
                                         final Duration checkpointDuration,
                                         final Long checkpointRecords) {
    this.changeEventIterator = changeEventIterator;
    this.cdcStateHandler = cdcStateHandler;
    this.targetPosition = targetPosition;
    this.cdcMetadataInjector = cdcMetadataInjector;
    this.emittedAt = emittedAt;
    this.offsetManager = offsetManager;
    this.trackSchemaHistory = trackSchemaHistory;
    this.schemaHistoryManager = schemaHistoryManager;

    this.syncCheckpointDuration = checkpointDuration;
    this.syncCheckpointRecords = checkpointRecords;
    this.previousCheckpointOffset = (HashMap<String, String>) offsetManager.read();
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

    if (cdcStateHandler.isCdcCheckpointEnabled() && sendCheckpointMessage) {
      LOGGER.info("Sending CDC checkpoint state message.");
      final AirbyteMessage stateMessage = createStateMessage(checkpointOffsetToSend);
      previousCheckpointOffset.clear();
      previousCheckpointOffset.putAll(checkpointOffsetToSend);
      resetCheckpointValues();
      return stateMessage;
    }

    if (changeEventIterator.hasNext()) {
      final ChangeEvent<String, String> event = changeEventIterator.next();

      if (cdcStateHandler.isCdcCheckpointEnabled()) {
        if (checkpointOffsetToSend.size() == 0 &&
            (recordsLastSync >= syncCheckpointRecords ||
                Duration.between(dateTimeLastSync, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)) {
          // Using temporal variable to avoid reading teh offset twice, one in the condition and another in
          // the assignation
          try {
            final HashMap<String, String> temporalOffset = (HashMap<String, String>) offsetManager.read();
            if (!targetPosition.isSameOffset(previousCheckpointOffset, temporalOffset)) {
              checkpointOffsetToSend.putAll(temporalOffset);
            }
          } catch (final ConnectException e) {
            LOGGER.warn("Offset file is being written by Debezium. Skipping CDC checkpoint in this loop.");
          }
        }

        if (checkpointOffsetToSend.size() == 1
            && changeEventIterator.hasNext()
            && !targetPosition.isSnapshotEvent(event)
            && targetPosition.isRecordBehindOffset(checkpointOffsetToSend, event)) {
          sendCheckpointMessage = true;
        }
      }
      recordsLastSync++;
      return DebeziumEventUtils.toAirbyteMessage(event, cdcMetadataInjector, emittedAt);
    }

    isSyncFinished = true;
    return createStateMessage(offsetManager.read());
  }

  /**
   * Initialize or reset the checkpoint variables.
   */
  private void resetCheckpointValues() {
    sendCheckpointMessage = false;
    checkpointOffsetToSend.clear();
    recordsLastSync = 0L;
    dateTimeLastSync = OffsetDateTime.now();
  }

  /**
   * Creates {@link AirbyteStateMessage} while updating CDC data, used to checkpoint the state of the
   * process.
   *
   * @return {@link AirbyteStateMessage} which includes offset and schema history if used.
   */
  private AirbyteMessage createStateMessage(final Map<String, String> offset) {
    if (trackSchemaHistory && schemaHistoryManager == null) {
      throw new RuntimeException("Schema History Tracking is true but manager is not initialised");
    }
    if (offsetManager == null) {
      throw new RuntimeException("Offset can not be null");
    }

    return cdcStateHandler.saveState(offset, schemaHistoryManager != null ? schemaHistoryManager.read() : null);
  }

}
