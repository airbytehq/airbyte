/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.NAMESPACE;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.RECORD_MESSAGE_1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.RECORD_MESSAGE_2;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.RECORD_MESSAGE_3;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.STREAM_NAME1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.XMIN_STATUS1;
import static io.airbyte.integrations.source.postgres.xmin.XminTestConstants.createStateMessage1WithCount;
import static org.junit.Assert.assertThrows;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Iterator;
import org.junit.jupiter.api.Test;

public class XminSourceStateIteratorTest {

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
    final XminStateManager manager = new XminStateManager(null);
    manager.setCurrentXminStatus(XMIN_STATUS1);
    final ConfiguredAirbyteStream stream =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withNamespace(NAMESPACE).withName(STREAM_NAME1));
    final SourceStateIterator iterator = new SourceStateIterator(
        messageIterator,
        stream,
        manager,
        new StateEmitFrequency(0L, Duration.ofSeconds(1L)));

    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(createStateMessage1WithCount(2.0), iterator.next());
    assertFalse(iterator.hasNext());
  }

  @Test
  void testSyncFail() {
    messageIterator = MoreIterators.of(RECORD_MESSAGE_1, RECORD_MESSAGE_2);
    final XminStateManager manager = new XminStateManager(null);
    manager.setCurrentXminStatus(XMIN_STATUS1);
    final ConfiguredAirbyteStream stream =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withNamespace(NAMESPACE).withName(STREAM_NAME1));
    final SourceStateIterator iterator = new SourceStateIterator(
        createExceptionIterator(),
        stream,
        manager,
        new StateEmitFrequency(0L, Duration.ofSeconds(1L)));

    assertEquals(RECORD_MESSAGE_1, iterator.next());
    assertEquals(RECORD_MESSAGE_2, iterator.next());
    assertEquals(RECORD_MESSAGE_3, iterator.next());
    // We want to throw an exception here.
    assertThrows(RuntimeException.class, () -> iterator.hasNext());
  }

}
