/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.util.Collections;
import java.util.Iterator;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class StateDecoratingIteratorTest {

  private static final String NAMESPACE = "public";
  private static final String STREAM_NAME = "shoes";
  private static final AirbyteStreamNameNamespacePair NAME_NAMESPACE_PAIR = new AirbyteStreamNameNamespacePair(STREAM_NAME, NAMESPACE);
  private static final String UUID_FIELD_NAME = "ascending_inventory_uuid";

  private static final AirbyteMessage EMPTY_STATE_MESSAGE = new AirbyteMessage().withType(Type.STATE);

  private static final String RECORD_VALUE_1 = "abc";
  private static final AirbyteMessage RECORD_MESSAGE_1 = createRecordMessage(RECORD_VALUE_1);
  private static final AirbyteMessage STATE_MESSAGE_1 = createStateMessage(RECORD_VALUE_1);

  private static final String RECORD_VALUE_2 = "def";
  private static final AirbyteMessage RECORD_MESSAGE_2 = createRecordMessage(RECORD_VALUE_2);
  private static final AirbyteMessage STATE_MESSAGE_2 = createStateMessage(RECORD_VALUE_2);

  private static final String RECORD_VALUE_3 = "xyz";
  private static final AirbyteMessage RECORD_MESSAGE_3 = createRecordMessage(RECORD_VALUE_3);
  private static final AirbyteMessage STATE_MESSAGE_3 = createStateMessage(RECORD_VALUE_3);

  private static AirbyteMessage createRecordMessage(final String recordValue) {
    return new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.jsonNode(ImmutableMap.of(UUID_FIELD_NAME, recordValue))));
  }

  private static AirbyteMessage createStateMessage(final String recordValue) {
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withData(Jsons.jsonNode(ImmutableMap.of("cursor", recordValue))));
  }

  private static Iterator<AirbyteMessage> messageIterator;
  private StateManager stateManager;

  @BeforeEach
  void setup() {
    stateManager = mock(StateManager.class);
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, null)).thenReturn(EMPTY_STATE_MESSAGE.getState());
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, RECORD_VALUE_1)).thenReturn(STATE_MESSAGE_1.getState());
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, RECORD_VALUE_2)).thenReturn(STATE_MESSAGE_2.getState());
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, RECORD_VALUE_3)).thenReturn(STATE_MESSAGE_3.getState());

    when(stateManager.getOriginalCursorField(NAME_NAMESPACE_PAIR)).thenReturn(Optional.empty());
    when(stateManager.getOriginalCursor(NAME_NAMESPACE_PAIR)).thenReturn(Optional.empty());
    when(stateManager.getCursorField(NAME_NAMESPACE_PAIR)).thenReturn(Optional.empty());
    when(stateManager.getCursor(NAME_NAMESPACE_PAIR)).thenReturn(Optional.empty());
  }

  @Test
  void testWithoutInitialCursor() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2);
    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING,
        0);

    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(STATE_MESSAGE_2, iterator.next());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testWithInitialCursor() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2);
    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        RECORD_VALUE_3,
        JsonSchemaPrimitive.STRING,
        0);

    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(STATE_MESSAGE_3, iterator.next());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testCursorFieldIsEmpty() {
    final AirbyteMessage recordMessage = Jsons.clone(RECORD_MESSAGE_1);
    ((ObjectNode) recordMessage.getRecord().getData()).remove(UUID_FIELD_NAME);
    final Iterator<AirbyteMessage> messageStream = MoreIterators.of(recordMessage);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageStream,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING,
        0);

    assertEquals(recordMessage, iterator.next());
    // null because no records with a cursor field were replicated for the stream.
    assertNull(iterator.next().getState());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testEmptyStream() {
    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        Collections.emptyIterator(),
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING,
        0);

    assertEquals(EMPTY_STATE_MESSAGE, iterator.next());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testUnicodeNull() {
    final String recordValueWithNull = "abc\u0000";
    final AirbyteMessage recordMessageWithNull = createRecordMessage(recordValueWithNull);

    // UTF8 null \u0000 is removed from the cursor value in the state message
    final AirbyteMessage stateMessageWithNull = STATE_MESSAGE_1;
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, recordValueWithNull)).thenReturn(stateMessageWithNull.getState());

    messageIterator = MoreIterators.of(recordMessageWithNull);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING,
        0);

    assertEquals(recordMessageWithNull, iterator.next());
    assertEquals(stateMessageWithNull, iterator.next());
    assertFalse(iterator.hasNext());
  }

  @Test
  @DisplayName("When initial cursor is null, and emit state for every record")
  void testStateEmission1() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2, RECORD_MESSAGE_3);
    final StateDecoratingIterator iterator1 = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING,
        1);

    assertEquals(RECORD_MESSAGE_1, iterator1.next());
    assertEquals(STATE_MESSAGE_1, iterator1.next());
    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(STATE_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    // final state message should only be emitted once
    assertEquals(STATE_MESSAGE_3, iterator1.next());
    assertFalse(iterator1.hasNext());
  }

  @Test
  @DisplayName("When initial cursor is null, and emit state for every 2 records")
  void testStateEmission2() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2, RECORD_MESSAGE_3);
    final StateDecoratingIterator iterator1 = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING,
        2);

    assertEquals(RECORD_MESSAGE_1, iterator1.next());
    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(STATE_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(STATE_MESSAGE_3, iterator1.next());
    assertFalse(iterator1.hasNext());
  }

  @Test
  @DisplayName("When initial cursor is not null")
  void testStateEmission3() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_2, RECORD_MESSAGE_3);
    final StateDecoratingIterator iterator1 = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        RECORD_VALUE_1,
        JsonSchemaPrimitive.STRING,
        1);

    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(STATE_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(STATE_MESSAGE_3, iterator1.next());
    assertFalse(iterator1.hasNext());
  }

}
