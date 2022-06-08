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

  private String maxCursor;
  private boolean hasEmittedState;

  public StateDecoratingIterator(final Iterator<AirbyteMessage> messageIterator,
                                 final StateManager stateManager,
                                 final AirbyteStreamNameNamespacePair pair,
                                 final String cursorField,
                                 final String initialCursor,
                                 final JsonSchemaPrimitive cursorType) {
    this.messageIterator = messageIterator;
    this.stateManager = stateManager;
    this.pair = pair;
    this.cursorField = cursorField;
    this.cursorType = cursorType;
    this.maxCursor = initialCursor;
  }

  @Override
  protected AirbyteMessage computeNext() {
    if (messageIterator.hasNext()) {
      final AirbyteMessage message = messageIterator.next();
      if (message.getRecord().getData().hasNonNull(cursorField)) {
        final String cursorCandidate = message.getRecord().getData().get(cursorField).asText();
        if (IncrementalUtils.compareCursors(maxCursor, cursorCandidate, cursorType) < 0) {
          maxCursor = cursorCandidate;
        }
      }

      return message;
    } else if (!hasEmittedState) {
      final AirbyteStateMessage stateMessage = stateManager.updateAndEmit(pair, maxCursor);
      LOGGER.info("State Report: stream name: {}, original cursor field: {}, original cursor {}, cursor field: {}, new cursor: {}",
          pair,
          stateManager.getOriginalCursorField(pair).orElse(null),
          stateManager.getOriginalCursor(pair).orElse(null),
          stateManager.getCursorField(pair).orElse(null),
          stateManager.getCursor(pair).orElse(null));
      if (stateManager.getCursor(pair).isEmpty()) {
        LOGGER.warn("Cursor was for stream {} was null. This stream will replicate all records on the next run", pair);
      }

      hasEmittedState = true;
      return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
    } else {
      return endOfData();
    }
  }

}
