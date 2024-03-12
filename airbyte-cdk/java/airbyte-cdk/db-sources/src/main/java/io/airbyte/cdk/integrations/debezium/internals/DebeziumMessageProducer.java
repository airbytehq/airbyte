/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import io.airbyte.cdk.integrations.debezium.CdcStateHandler;
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.HashMap;
import java.util.Map;
import org.apache.kafka.connect.errors.ConnectException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DebeziumMessageProducer<T> implements SourceStateMessageProducer<ChangeEventWithMetadata> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumMessageProducer.class);

  private final CdcStateHandler cdcStateHandler;

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
  private final HashMap<String, String> initialOffset, previousCheckpointOffset;
  private final AirbyteFileOffsetBackingStore offsetManager;
  private final CdcTargetPosition<T> targetPosition;
  private final boolean trackSchemaHistory;
  private final AirbyteSchemaHistoryStorage schemaHistoryManager;

  private boolean sendCheckpointMessage = false;

  private final DebeziumEventConverter eventConverter;

  public DebeziumMessageProducer(
                                 final CdcStateHandler cdcStateHandler,
                                 final CdcTargetPosition targetPosition,
                                 final DebeziumEventConverter eventConverter,
                                 final AirbyteFileOffsetBackingStore offsetManager,
                                 final boolean trackSchemaHistory,
                                 final AirbyteSchemaHistoryStorage schemaHistoryManager) {
    this.cdcStateHandler = cdcStateHandler;
    this.targetPosition = targetPosition;
    this.eventConverter = eventConverter;
    this.offsetManager = offsetManager;
    this.trackSchemaHistory = trackSchemaHistory;
    this.schemaHistoryManager = schemaHistoryManager;
    this.previousCheckpointOffset = (HashMap<String, String>) offsetManager.read();
    this.initialOffset = new HashMap<>(this.previousCheckpointOffset);
    resetCheckpointValues();
  }

  /**
   * @param stream
   * @return
   */
  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(ConfiguredAirbyteStream stream) {
    LOGGER.info("Sending CDC checkpoint state message.");
    final AirbyteStateMessage stateMessage = createStateMessage(checkpointOffsetToSend);
    previousCheckpointOffset.clear();
    previousCheckpointOffset.putAll(checkpointOffsetToSend);
    sendCheckpointMessage = false;
    return stateMessage;
  }

  /**
   * @param stream
   * @param message
   * @return
   */
  @Override
  public AirbyteMessage processRecordMessage(ConfiguredAirbyteStream stream, ChangeEventWithMetadata message) {

    if (checkpointOffsetToSend.isEmpty()) {
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
        && !message.isSnapshotEvent()) {
      if (targetPosition.isEventAheadOffset(checkpointOffsetToSend, message)) {
        sendCheckpointMessage = true;
      } else {
        LOGGER.info("Encountered records with the same event offset.");
      }
    }

    return eventConverter.toAirbyteMessage(message);
  }

  /**
   * @param stream
   * @return
   */
  @Override
  public AirbyteStateMessage createFinalStateMessage(ConfiguredAirbyteStream stream) {
    final var syncFinishedOffset = (HashMap<String, String>) offsetManager.read();

    System.out.println("initialoffset: " + initialOffset);
    System.out.println("syncFinishedOffset: " + syncFinishedOffset);

    if (targetPosition.isSameOffset(initialOffset, syncFinishedOffset)) {
      // Edge case where no progress has been made: wrap up the
      // sync by returning the initial offset instead of the
      // current offset. We do this because we found that
      // for some databases, heartbeats will cause Debezium to
      // overwrite the offset file with a state which doesn't
      // include all necessary data such as snapshot completion.
      // This is the case for MS SQL Server, at least.
      return createStateMessage(initialOffset);
    }
    return createStateMessage(syncFinishedOffset);
  }

  private void resetCheckpointValues() {
    checkpointOffsetToSend.clear();
  }

  /**
   * @param stream
   * @return
   */
  @Override
  public boolean shouldEmitStateMessage(ConfiguredAirbyteStream stream) {
    return cdcStateHandler.isCdcCheckpointEnabled() && sendCheckpointMessage;
  }

  /**
   * Creates {@link AirbyteStateMessage} while updating CDC data, used to checkpoint the state of the
   * process.
   *
   * @return {@link AirbyteStateMessage} which includes offset and schema history if used.
   */
  private AirbyteStateMessage createStateMessage(final Map<String, String> offset) {
    if (trackSchemaHistory && schemaHistoryManager == null) {
      throw new RuntimeException("Schema History Tracking is true but manager is not initialised");
    }
    if (offsetManager == null) {
      throw new RuntimeException("Offset can not be null");
    }

    final AirbyteStateMessage message =
        cdcStateHandler.saveState(offset, schemaHistoryManager != null ? schemaHistoryManager.read() : null).getState();
    return message;
  }

}
