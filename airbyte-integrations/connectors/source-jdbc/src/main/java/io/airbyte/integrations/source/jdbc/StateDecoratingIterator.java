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
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
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
    } else if (!hasEmittedState) {
      final AirbyteStateMessage stateMessage = stateManager.updateAndEmit(streamName, maxCursor);
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
    } else {
      return endOfData();
    }
  }

  // fixme (cgardens) - this is a hotfix for this issue:
  // https://github.com/airbytehq/airbyte/issues/1582. the correct fix is still in progress. this will
  // be temporary.
  public static Stream<AirbyteMessage> stream(Stream<AirbyteMessage> stream,
                                              JdbcStateManager stateManager,
                                              String streamName,
                                              String cursorField,
                                              String initialCursor,
                                              JsonSchemaPrimitive cursorType) {
    final AtomicReference<String> maxCursor = new AtomicReference<>(initialCursor);

    // 1. translate message stream into a message supplier stream so that it matches the type of the
    // operation that will create the state message.
    // 2. perform all of the operations of computeNext() to track the max cursor field.
    final Stream<Supplier<AirbyteMessage>> messageStream = stream.map(message -> {
      return () -> {
        final String cursorCandidate = message.getRecord().getData().get(cursorField).asText();
        if (IncrementalUtils.compareCursors(maxCursor.get(), cursorCandidate, cursorType) < 0) {
          maxCursor.set(cursorCandidate);
        }

        return message;
      };
    });

    // create a stream of one element that supplies the state message based on the side effects of the
    // entire message stream running.
    final Stream<Supplier<AirbyteMessage>> stateStream = Stream.of(() -> {
      final AirbyteStateMessage stateMessage = stateManager.updateAndEmit(streamName, maxCursor.get());
      return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
    });

    // smash the two streams together.
    return Stream.concat(messageStream, stateStream).map(Supplier::get);
  }

}
