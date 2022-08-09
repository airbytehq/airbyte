/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import com.google.common.collect.AbstractIterator;
import io.airbyte.db.IncrementalUtils;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class StateDecoratingIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(StateDecoratingIterator.class);

  private final Iterator<AirbyteMessage> messageIterator;
  private final StateManager stateManager;
  private final AirbyteStreamNameNamespacePair pair;
  private final String cursorField;
  private final JsonSchemaPrimitive cursorType;
  private final int stateEmissionFrequency;

  private String maxCursor;
  private boolean hasEmittedFinalState;

  // The intermediateStateMessage is set to the latest state message.
  // For every stateEmissionFrequency messages, emitIntermediateState is set to true and
  // the latest intermediateStateMessage will be emitted.
  private int totalRecordCount;
  private boolean emitIntermediateState = false;
  private AirbyteMessage intermediateStateMessage;

  /**
   * @param stateEmissionFrequency If larger than 0, intermediate states will be emitted for every
   *        stateEmissionFrequency records. Only emit intermediate states if the records are sorted by
   *        the cursor field.
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
    this.maxCursor = initialCursor;
    this.stateEmissionFrequency = stateEmissionFrequency;
  }

  private String getCursorCandidate(final AirbyteMessage message) {
    final String cursorCandidate = message.getRecord().getData().get(cursorField).asText();
    return (cursorCandidate != null ? cursorCandidate.replaceAll("\u0000", "") : null);
  }

  @Override
  protected AirbyteMessage computeNext() {
    if (emitIntermediateState && intermediateStateMessage != null) {
      final AirbyteMessage message = intermediateStateMessage;
      intermediateStateMessage = null;
      emitIntermediateState = false;
      return message;
    } else if (messageIterator.hasNext()) {
      totalRecordCount++;
      final AirbyteMessage message = messageIterator.next();
      if (message.getRecord().getData().hasNonNull(cursorField)) {
        final String cursorCandidate = getCursorCandidate(message);
        final int cursorComparison = IncrementalUtils.compareCursors(maxCursor, cursorCandidate, cursorType);
        if (cursorComparison < 0) {
          if (stateEmissionFrequency > 0) {
            intermediateStateMessage = createStateMessage(!messageIterator.hasNext());
          }
          maxCursor = cursorCandidate;
        }
      }

      if (stateEmissionFrequency > 0 && totalRecordCount % stateEmissionFrequency == 0) {
        emitIntermediateState = true;
      }

      return message;
    } else if (!hasEmittedFinalState) {
      return createStateMessage(true);
    } else {
      return endOfData();
    }
  }

  public AirbyteMessage createStateMessage(final boolean isFinalState) {
    final AirbyteStateMessage stateMessage = stateManager.updateAndEmit(pair, maxCursor);
    LOGGER.info("State Report: stream name: {}, original cursor field: {}, original cursor value {}, cursor field: {}, new cursor value: {}",
        pair,
        stateManager.getOriginalCursorField(pair).orElse(null),
        stateManager.getOriginalCursor(pair).orElse(null),
        stateManager.getCursorField(pair).orElse(null),
        stateManager.getCursor(pair).orElse(null));

    if (isFinalState) {
      hasEmittedFinalState = true;
      if (stateManager.getCursor(pair).isEmpty()) {
        LOGGER.warn("Cursor was for stream {} was null. This stream will replicate all records on the next run", pair);
      }
    }

    return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
  }

}
