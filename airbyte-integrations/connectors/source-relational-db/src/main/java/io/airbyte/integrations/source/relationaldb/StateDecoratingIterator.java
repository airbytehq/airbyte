/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import com.google.common.collect.AbstractIterator;
import io.airbyte.db.IncrementalUtils;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Iterator;
import java.util.Objects;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class StateDecoratingIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(StateDecoratingIterator.class);

  private final Iterator<AirbyteMessage> messageIterator;
  private final StateManager stateManager;
  private final AirbyteStreamNameNamespacePair pair;
  private final String cursorField;
  private final JsonSchemaPrimitive cursorType;

  private final String initialCursor;
  private String currentMaxCursor;
  private long currentMaxCursorRecordCount = 0L;
  private boolean hasEmittedFinalState;

  /**
   * These parameters are for intermediate state message emission. We can emit an intermediate state
   * when the following two conditions are met.
   * <p/>
   * 1. The records are sorted by the cursor field. This is true when {@code stateEmissionFrequency} >
   * 0. This logic is guaranteed in {@code AbstractJdbcSource#queryTableIncremental}, in which an
   * "ORDER BY" clause is appended to the SQL query if {@code stateEmissionFrequency} > 0.
   * <p/>
   * 2. There is a cursor value that is ready for emission. A cursor value is "ready" if there is no
   * more record with the same value. We cannot emit a cursor at will, because there may be multiple
   * records with the same cursor value. If we emit a cursor ignoring this condition, should the sync
   * fail right after the emission, the next sync may skip some records with the same cursor value due
   * to "WHERE cursor_field > cursor" in {@code AbstractJdbcSource#queryTableIncremental}.
   * <p/>
   * The {@code intermediateStateMessage} is set to the latest state message that is ready for
   * emission. For every {@code stateEmissionFrequency} messages, {@code emitIntermediateState} is set
   * to true and the latest "ready" state will be emitted in the next {@code computeNext} call.
   */
  private final int stateEmissionFrequency;
  private int totalRecordCount = 0;
  private boolean emitIntermediateState = false;
  private AirbyteMessage intermediateStateMessage = null;
  private boolean hasCaughtException = false;

  /**
   * @param stateManager Manager that maintains connector state
   * @param pair Stream Name and Namespace (e.g. public.users)
   * @param cursorField Path to the comparator field used to track the records read so far
   * @param initialCursor name of the initial cursor column
   * @param cursorType ENUM type of primitive values that can be used as a cursor for checkpointing
   * @param stateEmissionFrequency If larger than 0, the records are sorted by the cursor field, and
   *        intermediate states will be emitted for every {@code stateEmissionFrequency} records. The
   *        order of the records is guaranteed in {@code AbstractJdbcSource#queryTableIncremental}, in
   *        which an "ORDER BY" clause is appended to the SQL query if {@code stateEmissionFrequency}
   *        > 0.
   */
  public StateDecoratingIterator(final Iterator<AirbyteMessage> messageIterator,
                                 final StateManager stateManager,
                                 final AirbyteStreamNameNamespacePair pair,
                                 final String cursorField,
                                 final String initialCursor,
                                 final JsonSchemaPrimitive cursorType,
                                 final int stateEmissionFrequency) {
    this.messageIterator = messageIterator;
    this.stateManager = stateManager;
    this.pair = pair;
    this.cursorField = cursorField;
    this.cursorType = cursorType;
    this.initialCursor = initialCursor;
    this.currentMaxCursor = initialCursor;
    this.stateEmissionFrequency = stateEmissionFrequency;
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

  /**
   * Computes the next record retrieved from Source stream. Emits StateMessage containing data of the
   * record that has been read so far
   *
   * <p>
   * If this method throws an exception, it will propagate outward to the {@code hasNext} or
   * {@code next} invocation that invoked this method. Any further attempts to use the iterator will
   * result in an {@link IllegalStateException}.
   * </p>
   *
   * @return {@link AirbyteStateMessage} containing information of the records read so far
   */
  @Override
  protected AirbyteMessage computeNext() {
    if (hasCaughtException) {
      // Mark iterator as done since the next call to messageIterator will result in an
      // IllegalArgumentException and resets exception caught state.
      // This occurs when the previous iteration emitted state so this iteration cycle will indicate
      // iteration is complete
      hasCaughtException = false;
      return endOfData();
    }

    if (messageIterator.hasNext()) {
      Optional<AirbyteMessage> optionalIntermediateMessage = getIntermediateMessage();
      if (optionalIntermediateMessage.isPresent()) {
        return optionalIntermediateMessage.get();
      }

      totalRecordCount++;
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        final AirbyteMessage message = messageIterator.next();
        if (message.getRecord().getData().hasNonNull(cursorField)) {
          final String cursorCandidate = getCursorCandidate(message);
          final int cursorComparison = IncrementalUtils.compareCursors(currentMaxCursor, cursorCandidate, cursorType);
          if (cursorComparison < 0) {
            // Update the current max cursor only when current max cursor < cursor candidate from the message
            if (stateEmissionFrequency > 0 && !Objects.equals(currentMaxCursor, initialCursor) && messageIterator.hasNext()) {
              // Only emit an intermediate state when it is not the first or last record message,
              // because the last state message will be taken care of in a different branch.
              intermediateStateMessage = createStateMessage(false, totalRecordCount);
            }
            currentMaxCursor = cursorCandidate;
            currentMaxCursorRecordCount = 1L;
          } else if (cursorComparison == 0) {
            currentMaxCursorRecordCount++;
          }
        }

        if (stateEmissionFrequency > 0 && totalRecordCount % stateEmissionFrequency == 0) {
          emitIntermediateState = true;
        }

        return message;
      } catch (final Exception e) {
        emitIntermediateState = true;
        hasCaughtException = true;
        LOGGER.error("Message iterator failed to read next record.", e);
        optionalIntermediateMessage = getIntermediateMessage();
        return optionalIntermediateMessage.orElse(endOfData());
      }
    } else if (!hasEmittedFinalState) {
      return createStateMessage(true, totalRecordCount);
    } else {
      return endOfData();
    }
  }

  /**
   * Returns AirbyteStateMessage when in a ready state, a ready state means that it has satifies the
   * conditions of:
   * <p>
   * cursorField has changed (e.g. 08-22-2022 -> 08-23-2022) and there have been at least
   * stateEmissionFrequency number of records since the last emission
   * </p>
   *
   * @return AirbyteStateMessage if one exists, otherwise Optional indicating state was not ready to
   *         be emitted
   */
  protected final Optional<AirbyteMessage> getIntermediateMessage() {
    if (emitIntermediateState && intermediateStateMessage != null) {
      final AirbyteMessage message = intermediateStateMessage;
      intermediateStateMessage = null;
      emitIntermediateState = false;
      return Optional.of(message);
    }
    return Optional.empty();
  }

  /**
   * Creates AirbyteStateMessage while updating the cursor used to checkpoint the state of records
   * read up so far
   *
   * @param isFinalState marker for if the final state of the iterator has been reached
   * @param totalRecordCount count of read messages
   * @return AirbyteMessage which includes information on state of records read so far
   */
  public AirbyteMessage createStateMessage(final boolean isFinalState, int totalRecordCount) {
    final AirbyteStateMessage stateMessage = stateManager.updateAndEmit(pair, currentMaxCursor, currentMaxCursorRecordCount);
    final Optional<CursorInfo> cursorInfo = stateManager.getCursorInfo(pair);
    // logging once every 100 messages to reduce log verbosity
    if (totalRecordCount % 100 == 0) {
      LOGGER.info("State report for stream {} - original: {} = {} (count {}) -> latest: {} = {} (count {})",
          pair,
          cursorInfo.map(CursorInfo::getOriginalCursorField).orElse(null),
          cursorInfo.map(CursorInfo::getOriginalCursor).orElse(null),
          cursorInfo.map(CursorInfo::getOriginalCursorRecordCount).orElse(null),
          cursorInfo.map(CursorInfo::getCursorField).orElse(null),
          cursorInfo.map(CursorInfo::getCursor).orElse(null),
          cursorInfo.map(CursorInfo::getCursorRecordCount).orElse(null));
    }
    if (isFinalState) {
      hasEmittedFinalState = true;
      if (stateManager.getCursor(pair).isEmpty()) {
        LOGGER.warn("Cursor for stream {} was null. This stream will replicate all records on the next run", pair);
      }
    }

    return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
  }

}
