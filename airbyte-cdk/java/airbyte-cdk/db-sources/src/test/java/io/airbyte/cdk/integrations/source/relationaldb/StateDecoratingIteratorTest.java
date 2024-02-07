/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbState;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.cdk.integrations.source.relationaldb.state.StreamStateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.sql.SQLException;
import java.util.Collections;
import java.util.Iterator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class StateDecoratingIteratorTest {

  private static final String NAMESPACE = "public";
  private static final String STREAM_NAME = "shoes";
  private static final AirbyteStreamNameNamespacePair NAME_NAMESPACE_PAIR = new AirbyteStreamNameNamespacePair(STREAM_NAME, NAMESPACE);
  private static final String UUID_FIELD_NAME = "ascending_inventory_uuid";

  private static final AirbyteMessage EMPTY_STATE_MESSAGE = createEmptyStateMessage(0.0);

  private static final String RECORD_VALUE_1 = "abc";
  private static final AirbyteMessage RECORD_MESSAGE_1 = createRecordMessage(RECORD_VALUE_1);

  private static final String RECORD_VALUE_2 = "def";
  private static final AirbyteMessage RECORD_MESSAGE_2 = createRecordMessage(RECORD_VALUE_2);

  private static final String RECORD_VALUE_3 = "ghi";
  private static final AirbyteMessage RECORD_MESSAGE_3 = createRecordMessage(RECORD_VALUE_3);

  private static final String RECORD_VALUE_4 = "jkl";
  private static final AirbyteMessage RECORD_MESSAGE_4 = createRecordMessage(RECORD_VALUE_4);

  private static final String RECORD_VALUE_5 = "xyz";
  private static final AirbyteMessage RECORD_MESSAGE_5 = createRecordMessage(RECORD_VALUE_5);

  private static AirbyteMessage createRecordMessage(final String recordValue) {
    return new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withData(Jsons.jsonNode(ImmutableMap.of(UUID_FIELD_NAME, recordValue))));
  }

  private static AirbyteMessage createStateMessage(final String recordValue, final long cursorRecordCount, final double statsRecordCount) {
    final DbStreamState dbStreamState = new DbStreamState()
        .withCursorField(Collections.singletonList(UUID_FIELD_NAME))
        .withCursor(recordValue)
        .withStreamName(STREAM_NAME)
        .withStreamNamespace(NAMESPACE);
    if (cursorRecordCount > 0) {
      dbStreamState.withCursorRecordCount(cursorRecordCount);
    }
    final DbState dbState = new DbState().withCdc(false).withStreams(Collections.singletonList(dbStreamState));
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME).withNamespace(NAMESPACE))
                .withStreamState(Jsons.jsonNode(dbStreamState)))
            .withData(Jsons.jsonNode(dbState))
            .withSourceStats(new AirbyteStateStats().withRecordCount(statsRecordCount)));
  }

  private static AirbyteMessage createEmptyStateMessage(final double statsRecordCount) {
    final DbStreamState dbStreamState = new DbStreamState()
        .withCursorField(Collections.singletonList(UUID_FIELD_NAME))
        .withStreamName(STREAM_NAME)
        .withStreamNamespace(NAMESPACE);

    final DbState dbState = new DbState().withCdc(false).withStreams(Collections.singletonList(dbStreamState));
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(new AirbyteStreamState()
                .withStreamDescriptor(new StreamDescriptor().withName(STREAM_NAME).withNamespace(NAMESPACE))
                .withStreamState(Jsons.jsonNode(dbStreamState)))
            .withData(Jsons.jsonNode(dbState))
            .withSourceStats(new AirbyteStateStats().withRecordCount(statsRecordCount)));
  }

  private Iterator<AirbyteMessage> createExceptionIterator() {
    return new Iterator<>() {

      final Iterator<AirbyteMessage> internalMessageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2,
          RECORD_MESSAGE_2, RECORD_MESSAGE_3);

      @Override
      public boolean hasNext() {
        return true;
      }

      @Override
      public AirbyteMessage next() {
        if (internalMessageIterator.hasNext()) {
          return internalMessageIterator.next();
        } else {
          // this line throws a RunTimeException wrapped around a SQLException to mimic the flow of when a
          // SQLException is thrown and wrapped in
          // StreamingJdbcDatabase#tryAdvance
          throw new RuntimeException(new SQLException("Connection marked broken because of SQLSTATE(080006)", "08006"));
        }
      }

    };
  };

  private static Iterator<AirbyteMessage> messageIterator;
  private StateManager stateManager;

  @BeforeEach
  void setup() {
    final AirbyteStream airbyteStream = new AirbyteStream().withNamespace(NAMESPACE).withName(STREAM_NAME);
    final ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream()
        .withStream(airbyteStream)
        .withCursorField(Collections.singletonList(UUID_FIELD_NAME));

    stateManager = new StreamStateManager(Collections.emptyList(),
        new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(configuredAirbyteStream)));
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
    assertEquals(createStateMessage(RECORD_VALUE_2, 1, 2.0), iterator.next());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testWithInitialCursor() {
    // record 1 and 2 has smaller cursor value, so at the end, the initial cursor is emitted with 0
    // record count

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
    assertEquals(createStateMessage(RECORD_VALUE_5, 0, 2.0), iterator.next());
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
    assertEquals(createEmptyStateMessage(1.0), iterator.next());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testIteratorCatchesExceptionWhenEmissionFrequencyNonZero() {
    final Iterator<AirbyteMessage> exceptionIterator = createExceptionIterator();
    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        exceptionIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        RECORD_VALUE_1,
        JsonSchemaPrimitive.STRING,
        1);
    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    // continues to emit RECORD_MESSAGE_2 since cursorField has not changed thus not satisfying the
    // condition of "ready"
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(RECORD_MESSAGE_3, iterator.next());
    // emits the first state message since the iterator has changed cursorFields (2 -> 3) and met the
    // frequency minimum of 1 record
    assertEquals(createStateMessage(RECORD_VALUE_2, 2, 4.0), iterator.next());
    // no further records to read since Exception was caught above and marked iterator as endOfData()
    assertFalse(iterator.hasNext());
  }

  @Test
  void testIteratorCatchesExceptionWhenEmissionFrequencyZero() {
    final Iterator<AirbyteMessage> exceptionIterator = createExceptionIterator();
    final StateDecoratingIterator iterator = new StateDecoratingIterator(
        exceptionIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        RECORD_VALUE_1,
        JsonSchemaPrimitive.STRING,
        0);
    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(RECORD_MESSAGE_3, iterator.next());
    // since stateEmission is not set to emit frequently, this will catch the error but not emit state
    // message since it wasn't in a ready state
    // of having a frequency > 0 but will prevent an exception from causing the iterator to fail by
    // marking iterator as endOfData()
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
    assertEquals(createStateMessage(RECORD_VALUE_1, 1, 1.0), iterator.next());
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
    assertEquals(createStateMessage(RECORD_VALUE_1, 1, 2.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_2, 1, 1.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_4, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_3, 1, 1.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    // state 4 is not emitted because there is no more record and only
    // the final state should be emitted at this point; also the final
    // state should only be emitted once
    assertEquals(createStateMessage(RECORD_VALUE_5, 1, 1.0), iterator1.next());
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
    assertEquals(createStateMessage(RECORD_VALUE_1, 1, 2.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_4, iterator1.next());
    // emit state 3 because it is the latest state ready for emission
    assertEquals(createStateMessage(RECORD_VALUE_3, 1, 2.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_5, 1, 1.0), iterator1.next());
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
    assertEquals(createStateMessage(RECORD_VALUE_2, 1, 2.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_4, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_3, 1, 1.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_5, 1, 1.0), iterator1.next());
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
   * been synced to destination. Reference:
   * <a href="https://github.com/airbytehq/airbyte/issues/15427">link</a>
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
    assertEquals(createStateMessage(RECORD_VALUE_2, 2, 3.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_4, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_3, 3, 3.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_4, 1, 1.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_5, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_5, 2, 1.0), iterator1.next());
    assertFalse(iterator1.hasNext());
  }

  @Test
  void testStateEmissionForRecordsSharingSameCursorValueButDifferentStatsCount() {
    messageIterator = MoreIterators.of(
        RECORD_MESSAGE_2, RECORD_MESSAGE_2,
        RECORD_MESSAGE_2, RECORD_MESSAGE_2,
        RECORD_MESSAGE_3, RECORD_MESSAGE_3, RECORD_MESSAGE_3,
        RECORD_MESSAGE_3,
        RECORD_MESSAGE_3, RECORD_MESSAGE_3, RECORD_MESSAGE_3);
    final StateDecoratingIterator iterator1 = new StateDecoratingIterator(
        messageIterator,
        stateManager,
        NAME_NAMESPACE_PAIR,
        UUID_FIELD_NAME,
        RECORD_VALUE_1,
        JsonSchemaPrimitive.STRING,
        10);

    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_2, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    // state 2 is the latest state ready for emission because
    // all records with the same cursor value have been emitted
    assertEquals(createStateMessage(RECORD_VALUE_2, 4, 10.0), iterator1.next());
    assertEquals(RECORD_MESSAGE_3, iterator1.next());
    assertEquals(createStateMessage(RECORD_VALUE_3, 7, 1.0), iterator1.next());
    assertFalse(iterator1.hasNext());
  }

}
