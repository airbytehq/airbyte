package io.airbyte.cdk.integrations.source.relationaldb.state;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.cdk.integrations.source.relationaldb.StateDecoratingIterator;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import org.junit.jupiter.api.Test;

class CursorStateIteratorManagerTest {

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
}