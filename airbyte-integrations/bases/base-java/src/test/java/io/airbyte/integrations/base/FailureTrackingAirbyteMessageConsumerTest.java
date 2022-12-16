/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import org.junit.jupiter.api.Test;

class FailureTrackingAirbyteMessageConsumerTest {

  @Test
  void testStartNoFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());
    consumer.start();
    consumer.close();

    verify(consumer).close(false);
  }

  @Test
  void testStartWithFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());
    doThrow(new RuntimeException()).when(consumer).startTracked();

    // verify the exception still gets thrown.
    assertThrows(RuntimeException.class, consumer::start);
    consumer.close();

    verify(consumer).close(true);
  }

  @Test
  void testAcceptNoFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());

    final AirbyteMessage msg = mock(AirbyteMessage.class);
    consumer.accept(msg);
    consumer.close();

    verify(consumer).close(false);
  }

  @Test
  void testAcceptWithFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());
    final AirbyteMessage msg = mock(AirbyteMessage.class);
    when(msg.getType()).thenReturn(Type.RECORD);
    doThrow(new RuntimeException()).when(consumer).acceptTracked(any());

    // verify the exception still gets thrown.
    assertThrows(RuntimeException.class, () -> consumer.accept(msg));
    consumer.close();

    verify(consumer).close(true);
  }

  static class TestConsumer extends FailureTrackingAirbyteMessageConsumer {

    @Override
    protected void startTracked() {

    }

    @Override
    protected void acceptTracked(final AirbyteMessage s) {

    }

    @Override
    protected void close(final boolean hasFailed) {

    }

  }

}
