package io.airbyte.integrations.base;


import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import org.junit.jupiter.api.Test;

class FailureTrackingConsumerTest {
  @Test
  void testNoFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());
    consumer.accept("");
    consumer.close();

    verify(consumer).close(false);
  }

  @Test
  void testWithFailure() throws Exception {
    final TestConsumer consumer = spy(new TestConsumer());
    doThrow(new RuntimeException()).when(consumer).acceptTracked("");

    // verify the exception still gets thrown.
    assertThrows(RuntimeException.class, () -> consumer.accept(""));
    consumer.close();

    verify(consumer).close(true);
  }

  static class TestConsumer extends FailureTrackingConsumer<String> {

    @Override
    protected void acceptTracked(String s) {

    }

    @Override
    protected void close(boolean hasFailed) {

    }
  }
}
