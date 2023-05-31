/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.util.concurrent;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.List;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link ConcurrentStreamConsumer} class.
 */
class ConcurrentStreamConsumerTest {

  @Test
  void testAcceptMessage() throws InterruptedException {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer = mock(Consumer.class);

    final ConcurrentStreamConsumer concurrentStreamConsumer = new ConcurrentStreamConsumer(streamConsumer, 1);

    assertDoesNotThrow(() -> concurrentStreamConsumer.accept(stream));

    Thread.sleep(500);

    verify(streamConsumer, times(1)).accept(stream);
  }

  @Test
  void testAcceptMessageWithException() throws InterruptedException {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer = mock(Consumer.class);
    final Exception e = new NullPointerException("test");

    doThrow(e).when(streamConsumer).accept(any());

    final ConcurrentStreamConsumer concurrentStreamConsumer = new ConcurrentStreamConsumer(streamConsumer, 1);

    assertDoesNotThrow(() -> concurrentStreamConsumer.accept(stream));

    Thread.sleep(500);

    verify(streamConsumer, times(1)).accept(stream);
    assertTrue(concurrentStreamConsumer.getException().isPresent());
    assertEquals(e, concurrentStreamConsumer.getException().get());
    assertEquals(1, concurrentStreamConsumer.getExceptions().size());
    assertTrue(concurrentStreamConsumer.getExceptions().contains(e));
  }

  @Test
  void testAcceptMessageWithMultipleExceptions() throws InterruptedException {
    final AutoCloseableIterator<AirbyteMessage> stream1 = mock(AutoCloseableIterator.class);
    final AutoCloseableIterator<AirbyteMessage> stream2 = mock(AutoCloseableIterator.class);
    final AutoCloseableIterator<AirbyteMessage> stream3 = mock(AutoCloseableIterator.class);
    final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer = mock(Consumer.class);
    final Exception e1 = new NullPointerException("test1");
    final Exception e2 = new NullPointerException("test2");
    final Exception e3 = new NullPointerException("test3");

    doThrow(e1).when(streamConsumer).accept(stream1);
    doThrow(e2).when(streamConsumer).accept(stream2);
    doThrow(e3).when(streamConsumer).accept(stream3);

    final ConcurrentStreamConsumer concurrentStreamConsumer = new ConcurrentStreamConsumer(streamConsumer, 1);

    assertDoesNotThrow(() -> List.of(stream1, stream2, stream3).forEach(concurrentStreamConsumer::accept));

    Thread.sleep(500);

    verify(streamConsumer, times(3)).accept(any(AutoCloseableIterator.class));
    assertTrue(concurrentStreamConsumer.getException().isPresent());
    assertEquals(e1, concurrentStreamConsumer.getException().get());
    assertEquals(3, concurrentStreamConsumer.getExceptions().size());
    assertTrue(concurrentStreamConsumer.getExceptions().contains(e1));
    assertTrue(concurrentStreamConsumer.getExceptions().contains(e2));
    assertTrue(concurrentStreamConsumer.getExceptions().contains(e3));
  }

}
