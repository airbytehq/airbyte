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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.util.Optional;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class StateDecoratingIteratorTest {

  private static final String STREAM_NAME = "shoes";
  private static final String UUID_FIELD_NAME = "ascending_inventory_uuid";
  private static final AirbyteMessage RECORD_MESSAGE1 = new AirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new AirbyteRecordMessage()
          .withData(Jsons.jsonNode(ImmutableMap.of(UUID_FIELD_NAME, "abc"))));
  private static final AirbyteMessage RECORD_MESSAGE2 = new AirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new AirbyteRecordMessage()
          .withData(Jsons.jsonNode(ImmutableMap.of(UUID_FIELD_NAME, "def"))));

  private static Stream<AirbyteMessage> messageStream;
  private JdbcStateManager stateManager;
  private AirbyteStateMessage stateMessage;

  @BeforeEach
  void setup() {
    messageStream = Stream.of(RECORD_MESSAGE1, RECORD_MESSAGE2);
    stateManager = mock(JdbcStateManager.class);
    stateMessage = mock(AirbyteStateMessage.class);
    when(stateManager.getOriginalCursorField(STREAM_NAME)).thenReturn(Optional.empty());
    when(stateManager.getOriginalCursor(STREAM_NAME)).thenReturn(Optional.empty());
    when(stateManager.getCursorField(STREAM_NAME)).thenReturn(Optional.empty());
    when(stateManager.getCursor(STREAM_NAME)).thenReturn(Optional.empty());
  }

  @Test
  void test() {
    when(stateManager.updateAndEmit(STREAM_NAME, UUID_FIELD_NAME, "def")).thenReturn(stateMessage);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageStream,
        stateManager,
        STREAM_NAME,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING);

    assertEquals(RECORD_MESSAGE1, iterator.next());
    assertEquals(RECORD_MESSAGE2, iterator.next());
    assertEquals(stateMessage, iterator.next().getState());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testWithInitialCursor() {
    when(stateManager.updateAndEmit(STREAM_NAME, UUID_FIELD_NAME, "xyz")).thenReturn(stateMessage);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageStream,
        stateManager,
        STREAM_NAME,
        UUID_FIELD_NAME,
        "xyz",
        JsonSchemaPrimitive.STRING);

    assertEquals(RECORD_MESSAGE1, iterator.next());
    assertEquals(RECORD_MESSAGE2, iterator.next());
    assertEquals(stateMessage, iterator.next().getState());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testEmptyStream() {
    when(stateManager.updateAndEmit(STREAM_NAME, UUID_FIELD_NAME, null)).thenReturn(stateMessage);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        Stream.empty(),
        stateManager,
        STREAM_NAME,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING);

    assertEquals(stateMessage, iterator.next().getState());
    assertFalse(iterator.hasNext());
  }

}
