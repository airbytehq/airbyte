/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb.state;

import io.airbyte.cdk.db.IncrementalUtils;
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Objects;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CursorStateMessageProducer implements SourceStateMessageProducer<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CursorStateMessageProducer.class);
  private static final int LOG_FREQUENCY = 100;

  private final StateManager stateManager;
  private final Optional<String> initialCursor;
  private Optional<String> currentMaxCursor;

  // We keep this field to mark `cursor_record_count` and also to control logging frequency.
  private int currentCursorRecordCount = 0;
  private AirbyteStateMessage intermediateStateMessage = null;

  private boolean cursorOutOfOrderDetected = false;

  public CursorStateMessageProducer(final StateManager stateManager,
                                    final Optional<String> initialCursor) {
    this.stateManager = stateManager;
    this.initialCursor = initialCursor;
    this.currentMaxCursor = initialCursor;
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    // At this stage intermediate state message should never be null; otherwise it would have been
    // blocked by shouldEmitStateMessage check.
    final AirbyteStateMessage message = intermediateStateMessage;
    intermediateStateMessage = null;
    if (cursorOutOfOrderDetected) {
      LOGGER.warn("Intermediate state emission feature requires records to be processed in order according to the cursor value. Otherwise, "
          + "data loss can occur.");
    }
    return message;
  }

  /**
   * Note: We do not try to catch exception here. If error/exception happens, we should fail the sync,
   * and since we have saved state message before, we should be able to resume it in next sync if we
   * have fixed the underlying issue, of if the issue is transient.
   */
  @Override
  public AirbyteMessage processRecordMessage(final ConfiguredAirbyteStream stream, AirbyteMessage message) {
    final String cursorField = IncrementalUtils.getCursorField(stream);
    if (message.getRecord().getData().hasNonNull(cursorField)) {
      final String cursorCandidate = getCursorCandidate(cursorField, message);
      final JsonSchemaPrimitive cursorType = IncrementalUtils.getCursorType(stream,
          cursorField);
      final int cursorComparison = IncrementalUtils.compareCursors(currentMaxCursor.orElse(null), cursorCandidate, cursorType);
      if (cursorComparison < 0) {
        // Reset cursor but include current record message. This value will be used to create state message.
        // Update the current max cursor only when current max cursor < cursor candidate from the message
        if (!Objects.equals(currentMaxCursor, initialCursor)) {
          // Only create an intermediate state when it is not the first record.
          intermediateStateMessage = createStateMessage(stream);
        }
        currentMaxCursor = Optional.of(cursorCandidate);
        currentCursorRecordCount = 1;
      } else if (cursorComparison > 0) {
        cursorOutOfOrderDetected = true;
      } else {
        currentCursorRecordCount++;
      }
    }
    System.out.println("processed a record message. count: " + currentCursorRecordCount);
    return message;

  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    return createStateMessage(stream);
  }

  /**
   * Only sends out state message when there is a state message to be sent out.
   */
  @Override
  public boolean shouldEmitStateMessage(final ConfiguredAirbyteStream stream) {
    return intermediateStateMessage != null;
  }

  /**
   * Creates AirbyteStateMessage while updating the cursor used to checkpoint the state of records
   * read up so far
   *
   * @return AirbyteMessage which includes information on state of records read so far
   */
  private AirbyteStateMessage createStateMessage(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    System.out.println("state message creation: " + pair + " " + currentMaxCursor.orElse(null) + " " + currentCursorRecordCount);
    final AirbyteStateMessage stateMessage = stateManager.updateAndEmit(pair, currentMaxCursor.orElse(null), currentCursorRecordCount);
    final Optional<CursorInfo> cursorInfo = stateManager.getCursorInfo(pair);

    // logging once every 100 messages to reduce log verbosity
    if (currentCursorRecordCount % LOG_FREQUENCY == 0) {
      LOGGER.info("State report for stream {}: {}", pair, cursorInfo);
    }

    return stateMessage;
  }

  private String getCursorCandidate(final String cursorField, AirbyteMessage message) {
    final String cursorCandidate = message.getRecord().getData().get(cursorField).asText();
    return (cursorCandidate != null ? replaceNull(cursorCandidate) : null);
  }

  private String replaceNull(final String cursorCandidate) {
    if (cursorCandidate.contains("\u0000")) {
      return cursorCandidate.replaceAll("\u0000", "");
    }
    return cursorCandidate;
  }

}
