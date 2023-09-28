/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.util.concurrent;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.node.IntNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link ConcurrentStreamConsumer} class.
 */
class ConcurrentStreamConsumerTest {

  private static final String NAME = "name";
  private static final String NAMESPACE = "namespace";

  @Test
  void testAcceptMessage() {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer = mock(Consumer.class);

    final ConcurrentStreamConsumer concurrentStreamConsumer = new ConcurrentStreamConsumer(streamConsumer, 1);

    assertDoesNotThrow(() -> concurrentStreamConsumer.accept(List.of(stream)));

    verify(streamConsumer, times(1)).accept(stream);
  }

  @Test
  void testAcceptMessageWithException() {
    final AutoCloseableIterator<AirbyteMessage> stream = mock(AutoCloseableIterator.class);
    final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer = mock(Consumer.class);
    final Exception e = new NullPointerException("test");

    doThrow(e).when(streamConsumer).accept(any());

    final ConcurrentStreamConsumer concurrentStreamConsumer = new ConcurrentStreamConsumer(streamConsumer, 1);

    assertDoesNotThrow(() -> concurrentStreamConsumer.accept(List.of(stream)));

    verify(streamConsumer, times(1)).accept(stream);
    assertTrue(concurrentStreamConsumer.getException().isPresent());
    assertEquals(e, concurrentStreamConsumer.getException().get());
    assertEquals(1, concurrentStreamConsumer.getExceptions().size());
    assertTrue(concurrentStreamConsumer.getExceptions().contains(e));
  }

  @Test
  void testAcceptMessageWithMultipleExceptions() {
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

    assertDoesNotThrow(() -> concurrentStreamConsumer.accept(List.of(stream1, stream2, stream3)));

    verify(streamConsumer, times(3)).accept(any(AutoCloseableIterator.class));
    assertTrue(concurrentStreamConsumer.getException().isPresent());
    assertEquals(e1, concurrentStreamConsumer.getException().get());
    assertEquals(3, concurrentStreamConsumer.getExceptions().size());
    assertTrue(concurrentStreamConsumer.getExceptions().contains(e1));
    assertTrue(concurrentStreamConsumer.getExceptions().contains(e2));
    assertTrue(concurrentStreamConsumer.getExceptions().contains(e3));
  }

  @Test
  void testMoreStreamsThanAvailableThreads() {
    final List<Integer> baseData = List.of(2, 4, 6, 8, 10, 12, 14, 16, 18, 20);
    final List<AutoCloseableIterator<AirbyteMessage>> streams = new ArrayList<>();
    for (int i = 0; i < 20; i++) {
      final AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair =
          new AirbyteStreamNameNamespacePair(String.format("%s_%d", NAME, i), NAMESPACE);
      final List<AirbyteMessage> messages = new ArrayList<>();
      for (int d : baseData) {
        final AirbyteMessage airbyteMessage = mock(AirbyteMessage.class);
        final AirbyteRecordMessage recordMessage = mock(AirbyteRecordMessage.class);
        when(recordMessage.getData()).thenReturn(new IntNode(d * i));
        when(airbyteMessage.getRecord()).thenReturn(recordMessage);
        messages.add(airbyteMessage);
      }
      streams.add(AutoCloseableIterators.fromIterator(messages.iterator(), airbyteStreamNameNamespacePair));
    }
    final Consumer<AutoCloseableIterator<AirbyteMessage>> streamConsumer = mock(Consumer.class);

    final ConcurrentStreamConsumer concurrentStreamConsumer = new ConcurrentStreamConsumer(streamConsumer, streams.size());
    final Integer partitionSize = concurrentStreamConsumer.getParallelism();
    final List<List<AutoCloseableIterator<AirbyteMessage>>> partitions = Lists.partition(streams.stream().toList(),
        partitionSize);

    for (final List<AutoCloseableIterator<AirbyteMessage>> partition : partitions) {
      assertDoesNotThrow(() -> concurrentStreamConsumer.accept(partition));
    }

    verify(streamConsumer, times(streams.size())).accept(any(AutoCloseableIterator.class));
  }

}
