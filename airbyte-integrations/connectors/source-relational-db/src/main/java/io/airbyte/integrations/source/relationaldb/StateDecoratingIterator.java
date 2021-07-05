/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.relationaldb;

import com.google.common.collect.AbstractIterator;
import io.airbyte.db.IncrementalUtils;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
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

  public StateDecoratingIterator(Iterator<AirbyteMessage> messageIterator,
                                 StateManager stateManager,
                                 AirbyteStreamNameNamespacePair pair,
                                 String cursorField,
                                 String initialCursor,
                                 JsonSchemaPrimitive cursorType) {
    this.messageIterator = messageIterator;
    this.stateManager = stateManager;
    this.pair = pair;
    this.cursorField = cursorField;
    this.cursorType = cursorType;
    this.maxCursor = initialCursor;
    stateManager.setIsCdc(false);
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
