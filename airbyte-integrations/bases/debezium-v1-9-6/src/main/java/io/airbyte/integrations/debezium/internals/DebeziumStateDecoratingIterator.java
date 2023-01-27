/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.google.common.collect.AbstractIterator;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.time.Duration;
import java.time.OffsetDateTime;
import java.util.Iterator;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class encapsulates an iterator and adds the required functionality to create checkpoints for
 * CDC replications. That way, if the process fails in the middle of a long sync, the process is
 * able to recover for any acknowledged checkpoint in the following syncs.
 */
public class DebeziumStateDecoratingIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  public static final Duration SYNC_CHECKPOINT_DURATION = Duration.ofMinutes(10);
  public static final int SYNC_CHECKPOINT_RECORDS = 1000;

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumStateDecoratingIterator.class);

  private final Iterator<AirbyteMessage> messageIterator;
  private final CdcStateHandler cdcStateHandler;
  private final AirbyteFileOffsetBackingStore offsetManager;
  private final boolean trackSchemaHistory;
  private final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager;

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
  private Duration syncCheckpointDuration;
  private Integer syncCheckpointRecords;
  private OffsetDateTime dateTimeLastSync;
  private Integer recordsLastSync;
  private Map<String, String> checkpointOffset;
  private boolean sendCheckpointMessage;

  /**
   * @param messageIterator Base iterator that we want to enrich with checkpoint messages
   * @param cdcStateHandler Handler to save the offset and schema history
   * @param offsetManager Handler to read and write debezium offset file
   * @param trackSchemaHistory Set true if the schema needs to be tracked
   * @param schemaHistoryManager Handler to write schema. Needs to be initialized if
   *        trackSchemaHistory is set to true
   * @param checkpointDuration Duration between syncs
   * @param checkpointRecords Number of records between syncs
   */
  public DebeziumStateDecoratingIterator(final Iterator<AirbyteMessage> messageIterator,
                                         final CdcStateHandler cdcStateHandler,
                                         final AirbyteFileOffsetBackingStore offsetManager,
                                         final boolean trackSchemaHistory,
                                         final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager,
                                         final Duration checkpointDuration,
                                         final Integer checkpointRecords) {
    this.messageIterator = messageIterator;
    this.cdcStateHandler = cdcStateHandler;
    this.offsetManager = offsetManager;
    this.trackSchemaHistory = trackSchemaHistory;
    this.schemaHistoryManager = schemaHistoryManager;

    this.syncCheckpointDuration = checkpointDuration;
    this.syncCheckpointRecords = checkpointRecords;
    this.isSyncFinished = false;
    initializeCheckpointValues();
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
      initializeCheckpointValues();
      return stateMessage;
    }

    if (messageIterator.hasNext()) {
      try {
        AirbyteMessage message = messageIterator.next();
        recordsLastSync++;

        if (checkpointOffset == null &&
            (recordsLastSync >= syncCheckpointRecords ||
                Duration.between(dateTimeLastSync, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)) {
          checkpointOffset = offsetManager.read();
        }

        if (checkpointOffset != null && cdcStateHandler.isRecordBehindOffset(checkpointOffset, message)) {
          sendCheckpointMessage = true;
        }

        return message;
      } catch (final Exception e) {
        LOGGER.error("Message iterator failed to read next record. {}", e.getMessage());
      }
    }

    isSyncFinished = true;
    return createStateMessage(null);
  }

  /**
   * Initialize or reset the checkpoint variables.
   */
  private void initializeCheckpointValues() {
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
    final String dbHistory = trackSchemaHistory ? schemaHistoryManager
        .orElseThrow(() -> new RuntimeException("Schema History Tracking is true but manager is not initialised")).read() : null;
    return cdcStateHandler.saveState(offset != null ? offset : offsetManager.read(), dbHistory);
  }

}
