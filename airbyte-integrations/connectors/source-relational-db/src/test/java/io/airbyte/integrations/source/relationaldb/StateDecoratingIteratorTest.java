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
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class StateDecoratingIteratorTest {

  private static final String NAMESPACE = "public";
  private static final String STREAM_NAME = "shoes";
  private static final AirbyteStreamNameNamespacePair NAME_NAMESPACE_PAIR = new AirbyteStreamNameNamespacePair(STREAM_NAME, NAMESPACE);
  private static final String UUID_FIELD_NAME = "ascending_inventory_uuid";
  private static final AirbyteMessage RECORD_MESSAGE1 = new AirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new AirbyteRecordMessage()
          .withData(Jsons.jsonNode(ImmutableMap.of(UUID_FIELD_NAME, "abc"))));
  private static final AirbyteMessage RECORD_MESSAGE2 = new AirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new AirbyteRecordMessage()
          .withData(Jsons.jsonNode(ImmutableMap.of(UUID_FIELD_NAME, "def"))));

  private static Iterator<AirbyteMessage> messageIterator;
  private StateManager stateManager;
  private AirbyteStateMessage stateMessage;

  @BeforeEach
  void setup() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE1, RECORD_MESSAGE2);
    stateManager = mock(StateManager.class);
    stateMessage = mock(AirbyteStateMessage.class);
    when(stateManager.getOriginalCursorField(NAME_NAMESPACE_PAIR)).thenReturn(Optional.empty());
    when(stateManager.getOriginalCursor(NAME_NAMESPACE_PAIR)).thenReturn(Optional.empty());
    when(stateManager.getCursorField(NAME_NAMESPACE_PAIR)).thenReturn(Optional.empty());
    when(stateManager.getCursor(NAME_NAMESPACE_PAIR)).thenReturn(Optional.empty());
  }

  @Test
  void testWithoutInitialCursor() {
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, "def")).thenReturn(stateMessage);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
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
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, "xyz")).thenReturn(stateMessage);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        "xyz",
        JsonSchemaPrimitive.STRING);

    assertEquals(RECORD_MESSAGE1, iterator.next());
    assertEquals(RECORD_MESSAGE2, iterator.next());
    assertEquals(stateMessage, iterator.next().getState());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testCursorFieldIsEmpty() {
    final AirbyteMessage recordMessage = Jsons.clone(RECORD_MESSAGE1);
    ((ObjectNode) recordMessage.getRecord().getData()).remove(UUID_FIELD_NAME);
    final Iterator<AirbyteMessage> messageStream = MoreIterators.of(recordMessage);

    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, "xyz")).thenReturn(stateMessage);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        messageStream,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING);

    assertEquals(recordMessage, iterator.next());
    // null because no records with a cursor field were replicated for the stream.
    assertNull(iterator.next().getState());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testEmptyStream() {
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, null)).thenReturn(stateMessage);

    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        Collections.emptyIterator(),
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING);

    assertEquals(stateMessage, iterator.next().getState());
    assertFalse(iterator.hasNext());
  }

}
