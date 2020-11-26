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

package io.airbyte.integrations.source.jdbc;

import com.google.common.collect.AbstractIterator;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.util.Iterator;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class StateDecoratingIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(StateDecoratingIterator.class);

  private final Iterator<AirbyteMessage> messageStream;
  private final JdbcStateManager stateManager;
  private final String streamName;
  private final String cursorField;
  private final JsonSchemaPrimitive cursorType;

  private String maxCursor;
  private boolean hasEmittedState;

  public StateDecoratingIterator(
                                 Stream<AirbyteMessage> messageStream,
                                 JdbcStateManager stateManager,
                                 String streamName,
                                 String cursorField,
                                 String initialCursor,
                                 JsonSchemaPrimitive cursorType) {
    this.messageStream = messageStream.iterator();
    this.stateManager = stateManager;
    this.streamName = streamName;
    this.cursorField = cursorField;
    this.cursorType = cursorType;
    this.maxCursor = initialCursor;
  }

  @Override
  protected AirbyteMessage computeNext() {
    if (messageStream.hasNext()) {
      final AirbyteMessage message = messageStream.next();
      final String cursorCandidate = message.getRecord().getData().get(cursorField).asText();
      if (IncrementalUtils.compareCursors(maxCursor, cursorCandidate, cursorType) < 0) {
        maxCursor = cursorCandidate;
      }

      return message;
    }

    if (!hasEmittedState) {
      final AirbyteStateMessage stateMessage = stateManager.updateAndEmit(streamName, cursorField, maxCursor);
      LOGGER.info("State Report: stream name: {}, original cursor field: {}, original cursor {}, cursor field: {}, new cursor: {}",
          streamName,
          stateManager.getOriginalCursorField(streamName).orElse(null),
          stateManager.getOriginalCursor(streamName).orElse(null),
          stateManager.getCursorField(streamName).orElse(null),
          stateManager.getCursor(streamName).orElse(null));
      if (stateManager.getCursor(streamName).isEmpty()) {
        LOGGER.warn("Cursor was for stream {} was null. This stream will replicate all records on the next run", streamName);
      }

      hasEmittedState = true;
      return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
    }

    return endOfData();
  }

}
