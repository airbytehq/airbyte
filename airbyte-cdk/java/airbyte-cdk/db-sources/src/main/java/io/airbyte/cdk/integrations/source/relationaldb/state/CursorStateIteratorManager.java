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
import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CursorStateIteratorManager implements SourceStateIteratorManager<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CursorStateIteratorManager.class);

  private final StateManager stateManager;
  private final AirbyteStreamNameNamespacePair pair;
  private final String cursorField;
  private final JsonSchemaPrimitive cursorType;

  private final String initialCursor;
  private String currentMaxCursor;
  private long currentMaxCursorRecordCount = 0L;
  private final int stateEmissionFrequency;

  // We keep this field just to control logging frequency.
  private int totalRecordCount = 0;
  private AirbyteStateMessage intermediateStateMessage = null;

  public CursorStateIteratorManager(
                                    final StateManager stateManager,
                                    final AirbyteStreamNameNamespacePair pair,
                                    final String cursorField,
                                    final String initialCursor,
                                    final JsonSchemaPrimitive cursorType,
                                    final int stateEmissionFrequency) {
    this.stateManager = stateManager;
    this.pair = pair;
    this.cursorField = cursorField;
    this.cursorType = cursorType;
    this.initialCursor = initialCursor;
    this.currentMaxCursor = initialCursor;
    this.stateEmissionFrequency = stateEmissionFrequency;
  }

  /**
   * @return
   */
  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint() {
    // At this stage intermediate state message should never be null; otherwise it would have been
    // blocked by shouldEmitStateMessage check.
    final AirbyteStateMessage message = intermediateStateMessage;
    intermediateStateMessage = null;
    return null;
  }

  /**
   * Note: We do not try to catch exception here. If error/exception happens, we should fail the sync,
   * and since we have saved state message before, we should be able to resume it in next sync if we
   * have fixed the underlying issue, of if the issue is transient.
   *
   * @param message
   * @return
   */
  @Override
  public AirbyteMessage processRecordMessage(AirbyteMessage message) {
    totalRecordCount++;
    if (message.getRecord().getData().hasNonNull(cursorField)) {
      final String cursorCandidate = getCursorCandidate(message);
      final int cursorComparison = IncrementalUtils.compareCursors(currentMaxCursor, cursorCandidate, cursorType);
      if (cursorComparison < 0) {
        // Update the current max cursor only when current max cursor < cursor candidate from the message
        if (stateEmissionFrequency > 0 && !Objects.equals(currentMaxCursor, initialCursor)) {
          // Only create an intermediate state when it is not the first record.
          intermediateStateMessage = createStateMessage(totalRecordCount);
        }
        currentMaxCursor = cursorCandidate;
        currentMaxCursorRecordCount = 1L;
      } else if (cursorComparison == 0) {
        currentMaxCursorRecordCount++;
      } else if (cursorComparison > 0 && stateEmissionFrequency > 0) {
        LOGGER.warn("Intermediate state emission feature requires records to be processed in order according to the cursor value. Otherwise, "
            + "data loss can occur.");
      }
    }
    return message;

  }

  /**
   * @return
   */
  @Override
  public AirbyteStateMessage createFinalStateMessage() {
    return createStateMessage(totalRecordCount);
  }

  /**
   * @param recordCount
   * @param lastCheckpoint
   * @return
   */
  @Override
  public boolean shouldEmitStateMessage(long recordCount, Instant lastCheckpoint) {
    return intermediateStateMessage != null && stateEmissionFrequency > 0 && totalRecordCount % stateEmissionFrequency == 0;
  }

  /**
   * Creates AirbyteStateMessage while updating the cursor used to checkpoint the state of records
   * read up so far
   *
   * @param recordCount count of total read messages. Used to determine log frequency.
   * @return AirbyteMessage which includes information on state of records read so far
   */
  private AirbyteStateMessage createStateMessage(final int recordCount) {
    final AirbyteStateMessage stateMessage = stateManager.updateAndEmit(pair, currentMaxCursor, currentMaxCursorRecordCount);
    final Optional<CursorInfo> cursorInfo = stateManager.getCursorInfo(pair);

    // logging once every 100 messages to reduce log verbosity
    if (recordCount % 100 == 0) {
      LOGGER.info("State report for stream {} - original: {} = {} (count {}) -> latest: {} = {} (count {})",
          pair,
          cursorInfo.map(CursorInfo::getOriginalCursorField).orElse(null),
          cursorInfo.map(CursorInfo::getOriginalCursor).orElse(null),
          cursorInfo.map(CursorInfo::getOriginalCursorRecordCount).orElse(null),
          cursorInfo.map(CursorInfo::getCursorField).orElse(null),
          cursorInfo.map(CursorInfo::getCursor).orElse(null),
          cursorInfo.map(CursorInfo::getCursorRecordCount).orElse(null));
    }

    return stateMessage;
  }

  private String getCursorCandidate(final AirbyteMessage message) {
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
