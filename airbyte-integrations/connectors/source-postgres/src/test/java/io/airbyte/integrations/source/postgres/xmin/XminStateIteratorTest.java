/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.PAIR1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.RECORD_MESSAGE_1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.RECORD_MESSAGE_2;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.RECORD_MESSAGE_3;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.XMIN_STATE_MESSAGE_1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.XMIN_STATUS1;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.sql.SQLException;
import java.util.Iterator;
import org.junit.jupiter.api.Test;

public class XminStateIteratorTest {

  private static Iterator<AirbyteMessage> messageIterator;

  private Iterator<AirbyteMessage> createExceptionIterator() {
    return new Iterator<>() {

      final Iterator<AirbyteMessage> internalMessageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2,
          RECORD_MESSAGE_3);

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

  @Test
  void testSuccessfulSync() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2);
    final XminStateIterator iterator = new XminStateIterator(
        messageIterator,
        PAIR1,
        XMIN_STATUS1);

    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(XMIN_STATE_MESSAGE_1, iterator.next());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testSyncFail() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2);
    final XminStateIterator iterator = new XminStateIterator(
        createExceptionIterator(),
        PAIR1,
        XMIN_STATUS1);

    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(RECORD_MESSAGE_3, iterator.next());
    // No state message is emitted at this point.
    // Since there is no intermediate stateEmission, this will catch the error but not emit a state
    // message
    // but will prevent an exception from causing the iterator to fail by marking iterator as
    // endOfData()
    assertFalse(iterator.hasNext());
  }

}
