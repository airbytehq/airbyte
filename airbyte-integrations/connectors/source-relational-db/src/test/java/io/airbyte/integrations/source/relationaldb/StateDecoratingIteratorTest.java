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

  private static final String RECORD_VALUE_3 = "ghi";
  private static final AirbyteMessage RECORD_MESSAGE_3 = createRecordMessage(RECORD_VALUE_3);
  private static final AirbyteMessage STATE_MESSAGE_3 = createStateMessage(RECORD_VALUE_3);

  private static final String RECORD_VALUE_4 = "jkl";
  private static final AirbyteMessage RECORD_MESSAGE_4 = createRecordMessage(RECORD_VALUE_4);
  private static final AirbyteMessage STATE_MESSAGE_4 = createStateMessage(RECORD_VALUE_4);

  private static final String RECORD_VALUE_5 = "xyz";
  private static final AirbyteMessage RECORD_MESSAGE_5 = createRecordMessage(RECORD_VALUE_5);
  private static final AirbyteMessage STATE_MESSAGE_5 = createStateMessage(RECORD_VALUE_5);

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
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, RECORD_VALUE_4)).thenReturn(STATE_MESSAGE_4.getState());
    when(stateManager.updateAndEmit(NAME_NAMESPACE_PAIR, RECORD_VALUE_5)).thenReturn(STATE_MESSAGE_5.getState());

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
        RECORD_VALUE_5,
        JsonSchemaPrimitive.STRING,
        0);

    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(STATE_MESSAGE_5, iterator.next());
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
  void testStateEmissionFrequency1() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2, RECORD_MESSAGE_3, RECORD_MESSAGE_4, RECORD_MESSAGE_5);
    final StateDecoratingIterator iterator1 = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        null,
        JsonSchemaPrimitive.STRING,
        1);

    assertEquals(RECORD_MESSAGE_1, iterator1.next());
    // should emit state 1, but it is unclear whether there will be more
    // records with the same cursor value, so no state is ready for emission
    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    // emit state 1 because it is the latest state ready for emission
    assertEquals(STATE_MESSAGE_1, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(STATE_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_4, iterator1.next());
    assertEquals(STATE_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    // state 4 is not emitted because there is no more record and only
    // the final state should be emitted at this point; also the final
    // state should only be emitted once
    assertEquals(STATE_MESSAGE_5, iterator1.next());
    assertFalse(iterator1.hasNext());
  }

  @Test
  @DisplayName("When initial cursor is null, and emit state for every 2 records")
  void testStateEmissionFrequency2() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2, RECORD_MESSAGE_3, RECORD_MESSAGE_4, RECORD_MESSAGE_5);
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
    // emit state 1 because it is the latest state ready for emission
    assertEquals(STATE_MESSAGE_1, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_4, iterator1.next());
    // emit state 3 because it is the latest state ready for emission
    assertEquals(STATE_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    assertEquals(STATE_MESSAGE_5, iterator1.next());
    assertFalse(iterator1.hasNext());
  }

  @Test
  @DisplayName("When initial cursor is not null")
  void testStateEmissionWhenInitialCursorIsNotNull() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_2, RECORD_MESSAGE_3, RECORD_MESSAGE_4, RECORD_MESSAGE_5);
    final StateDecoratingIterator iterator1 = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        RECORD_VALUE_1,
        JsonSchemaPrimitive.STRING,
        1);

    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(STATE_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_4, iterator1.next());
    assertEquals(STATE_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    assertEquals(STATE_MESSAGE_5, iterator1.next());
    assertFalse(iterator1.hasNext());
  }

  /**
   * Incremental syncs will sort the table with the cursor field, and emit the max cursor for every N
   * records. The purpose is to emit the states frequently, so that if any transient failure occurs
   * during a long sync, the next run does not need to start from the beginning, but can resume from
   * the last successful intermediate state committed on the destination. The next run will start with
   * `cursorField > cursor`. However, it is possible that there are multiple records with the same
   * cursor value. If the intermediate state is emitted before all these records have been synced to
   * the destination, some of these records may be lost.
   * <p/>
   * Here is an example:
   *
   * <pre>
   * | Record ID | Cursor Field | Other Field | Note                          |
   * | --------- | ------------ | ----------- | ----------------------------- |
   * | 1         | F1=16        | F2="abc"    |                               |
   * | 2         | F1=16        | F2="def"    | <- state emission and failure |
   * | 3         | F1=16        | F2="ghi"    |                               |
   * </pre>
   *
   * If the intermediate state is emitted for record 2 and the sync fails immediately such that the
   * cursor value `16` is committed, but only record 1 and 2 are actually synced, the next run will
   * start with `F1 > 16` and skip record 3.
   * <p/>
   * So intermediate state emission should only happen when all records with the same cursor value has
   * been synced to destination. Reference: https://github.com/airbytehq/airbyte/issues/15427
   */
  @Test
  @DisplayName("When there are multiple records with the same cursor value")
  void testStateEmissionForRecordsSharingSameCursorValue() {
    messageIterator = MoreIterators.of(
        RECORD_MESSAGE_2, RECORD_MESSAGE_2,
        RECORD_MESSAGE_3, RECORD_MESSAGE_3, RECORD_MESSAGE_3,
        RECORD_MESSAGE_4,
        RECORD_MESSAGE_5, RECORD_MESSAGE_5);
    final StateDecoratingIterator iterator1 = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        RECORD_VALUE_1,
        JsonSchemaPrimitive.STRING,
        1);

    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    // state 2 is the latest state ready for emission because
    // all records with the same cursor value have been emitted
    assertEquals(STATE_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_4, iterator1.next());
    assertEquals(STATE_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    assertEquals(STATE_MESSAGE_4, iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    assertEquals(STATE_MESSAGE_5, iterator1.next());
    assertFalse(iterator1.hasNext());
  }

}
