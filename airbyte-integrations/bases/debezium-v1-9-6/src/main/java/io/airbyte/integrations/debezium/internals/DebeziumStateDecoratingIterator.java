/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.google.common.collect.AbstractIterator;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.time.OffsetDateTime;
import java.util.Iterator;
import java.util.Map;
import java.util.Optional;

/**
 * This class encapsulates an iterator and adds the required functionality to create checkpoints for CDC replications.
 * That way, if the process fails in the middle of a long sync, the process is able to recover for any acknowledged
 * checkpoint in the following syncs.
 */
public class DebeziumStateDecoratingIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumStateDecoratingIterator.class);

  private final Iterator<AirbyteMessage> messageIterator;
  private final CdcStateHandler cdcStateHandler;
  private final AirbyteFileOffsetBackingStore offsetManager;
  private final boolean trackSchemaHistory;
  private final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager;

  private boolean isSyncFinished;

  /**
   * These parameters control when a checkpoint message has to be sent in a CDC integration. We can emit a checkpoint
   * when any of the following two conditions are met.
   * <p/>
   * 1. The amount of records in the current loop ({@code SYNC_CHECKPOINT_RECORDS}) is higher than a threshold defined
   * by {@code SYNC_CHECKPOINT_RECORDS}.
   * <p/>
   * 2. Time between checkpoints ({@code dateTimeLastSync}) is higher than a {@code Duration} defined at
   * {@code SYNC_CHECKPOINT_SECONDS}.
   * <p/>
   */
  private final static Duration SYNC_CHECKPOINT_SECONDS = Duration.ofMinutes(10);
  private final static int SYNC_CHECKPOINT_RECORDS = 1000;

  //Properties used as checkpoint
  private OffsetDateTime dateTimeLastSync;
  private Integer recordsLastSync;

  /**
   * @param messageIterator      Base iterator that we want to enrich with checkpoint messages
   * @param cdcStateHandler      Handler to save the offset and schema history
   * @param offsetManager        Handler to read and write debezium offset file
   * @param trackSchemaHistory   Set true if the schema needs to be tracked
   * @param schemaHistoryManager Handler to write schema. Needs to be initialized if trackSchemaHistory is set to true
   */
  public DebeziumStateDecoratingIterator(
    final Iterator<AirbyteMessage> messageIterator,
    final CdcStateHandler cdcStateHandler,
    final AirbyteFileOffsetBackingStore offsetManager,
    final boolean trackSchemaHistory,
    final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager) {
    this.messageIterator = messageIterator;
    this.cdcStateHandler = cdcStateHandler;
    this.offsetManager = offsetManager;
    this.trackSchemaHistory = trackSchemaHistory;
    this.schemaHistoryManager = schemaHistoryManager;

    this.isSyncFinished = false;
    initializeCheckpointValues();
  }

  /**
   * Computes the next record retrieved from Source stream. Emits state messages as checkpoints based on number of
   * records or time lapsed.
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

    if (messageIterator.hasNext()) {
      if (recordsLastSync >= SYNC_CHECKPOINT_RECORDS ||
        Duration.between(dateTimeLastSync, OffsetDateTime.now()).compareTo(SYNC_CHECKPOINT_SECONDS) > 0) {
        AirbyteMessage stateMessage = createStateMessage();
        initializeCheckpointValues();
        return stateMessage;
      }

      recordsLastSync++;
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        return messageIterator.next();
      } catch (final Exception e) {
        LOGGER.error("Message iterator failed to read next record. {}", e.getMessage());
        //TODO: Check that the record that fails is not missed on next execution!
        isSyncFinished = true;
        return createStateMessage();
      }
    } else {
      isSyncFinished = true;
      return createStateMessage();
    }
  }

  /**
   * Initialize or reset the checkpoint variables.
   */
  private void initializeCheckpointValues() {
    this.recordsLastSync = 0;
    this.dateTimeLastSync = OffsetDateTime.now();
  }

  /**
   * Creates {@link AirbyteStateMessage} while updating CDC data, used to checkpoint the state of the process.
   *
   * @return {@link AirbyteStateMessage} which includes offset and schema history if used.
   */
  private AirbyteMessage createStateMessage() {
    final Map<String, String> offset = offsetManager.read();
    final String dbHistory = trackSchemaHistory ? schemaHistoryManager
      .orElseThrow(() -> new RuntimeException("Schema History Tracking is true but manager is not initialised")).read() : null;

    return cdcStateHandler.saveState(offset, dbHistory);
  }
}
