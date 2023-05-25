/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.lenient;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.junit.jupiter.MockitoExtension;

/**
 * Test suite for the {@link ParallelCompositeIterator} class.
 */
@ExtendWith(MockitoExtension.class)
class ParallelCompositeIteratorTest {

  public static final String NAMESPACE = "namespace";
  private VoidCallable onClose1;
  private VoidCallable onClose2;
  private VoidCallable onClose3;
  private Consumer airbyteStreamStatusConsumer;
  private AirbyteStreamNameNamespacePair airbyteStream1;
  private AirbyteStreamNameNamespacePair airbyteStream2;
  private AirbyteStreamNameNamespacePair airbyteStream3;
  @Captor
  private ArgumentCaptor<AirbyteStreamStatusHolder> airbyteStreamStatusHolderArgumentCaptor;

  @BeforeEach
  void setup() {
    onClose1 = mock(VoidCallable.class);
    onClose2 = mock(VoidCallable.class);
    onClose3 = mock(VoidCallable.class);
    airbyteStreamStatusConsumer = mock(Consumer.class);
    airbyteStream1 = new AirbyteStreamNameNamespacePair("stream1", NAMESPACE);
    airbyteStream2 = new AirbyteStreamNameNamespacePair("stream2", NAMESPACE);
    airbyteStream3 = new AirbyteStreamNameNamespacePair("stream3", NAMESPACE);
  }

  @Test
  void testNullInput() {
    assertDoesNotThrow(() -> new ParallelCompositeIterator<>(null, airbyteStreamStatusConsumer));
    verify(airbyteStreamStatusConsumer, times(0)).accept(any());
  }

  @Test
  void testEmptyInput() {
    final AutoCloseableIterator<String> iterator = new ParallelCompositeIterator<>(Collections.emptyList(), airbyteStreamStatusConsumer);
    assertFalse(iterator.hasNext());
    verify(airbyteStreamStatusConsumer, times(0)).accept(any());
  }

  @Test
  void testMultipleIterators() throws Exception {
    final Set<String> streamData1 = Set.of("a", "b", "c");
    final Set<String> streamData2 = Set.of("d", "e", "f");
    final Set<String> streamData3 = Set.of("g", "h", "i");
    final AutoCloseableIterator<String> iterator = new ParallelCompositeIterator<>(List.of(
        AutoCloseableIterators.fromIterator(streamData1.iterator(), onClose1, airbyteStream1),
        AutoCloseableIterators.fromIterator(streamData2.iterator(), onClose2, airbyteStream2),
        AutoCloseableIterators.fromIterator(streamData3.iterator(), onClose3, airbyteStream3)), airbyteStreamStatusConsumer);
    final Set<String> results = new HashSet<>();

    while (iterator.hasNext()) {
      results.add(iterator.next());
    }

    assertEquals(9, results.size());
    assertTrue(results.containsAll(streamData1));
    assertTrue(results.containsAll(streamData2));
    assertTrue(results.containsAll(streamData3));

    iterator.close();

    assertFalse(iterator.hasNext());
    verify(onClose1, times(1)).call();
    verify(onClose2, times(1)).call();
    verify(onClose3, times(1)).call();
    verify(airbyteStreamStatusConsumer, times(9)).accept(any());
  }

  @Test
  void testMultipleIteratorsMoreThanThreadPool() throws Exception {
    final String data = "abcdefghijklmnopqrstuvwxyz0123456789";
    final List<AirbyteStreamNameNamespacePair> streams = new ArrayList<>();
    final List<VoidCallable> closeHandlers = new ArrayList<>();
    final List<Set<String>> streamData = new ArrayList<>();
    final List<AutoCloseableIterator<String>> iterators = new ArrayList<>();

    IntStream.range(1, 13).forEach(i -> {
      final int index = i - 1;
      final int dataIndex = index * 3;
      streams.add(new AirbyteStreamNameNamespacePair("stream" + i, NAMESPACE));
      closeHandlers.add(mock(VoidCallable.class));
      streamData.add(data.substring(dataIndex, dataIndex + 3).chars().mapToObj(c -> String.valueOf((char) c)).collect(Collectors.toSet()));
      iterators.add(AutoCloseableIterators.fromIterator(streamData.get(index).iterator(), closeHandlers.get(index), streams.get(index)));
    });

    final AutoCloseableIterator<String> iterator = new ParallelCompositeIterator<>(iterators, airbyteStreamStatusConsumer);
    final Set<String> results = new HashSet<>();

    while (iterator.hasNext()) {
      results.add(iterator.next());
    }

    final int expectedDataCount = streamData.stream().mapToInt(s -> s.size()).sum();

    assertEquals(expectedDataCount, results.size());
    streamData.forEach(s -> assertTrue(results.containsAll(s)));

    iterator.close();

    assertFalse(iterator.hasNext());
    closeHandlers.forEach(c -> {
      try {
        verify(c, times(1)).call();
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
    verify(airbyteStreamStatusConsumer, times(expectedDataCount)).accept(any());
  }

  @Test
  void testSingleIterator() throws Exception {
    final Set<String> streamData1 = Set.of("a", "b", "c");
    final AutoCloseableIterator<String> iterator = new ParallelCompositeIterator<>(List.of(
        AutoCloseableIterators.fromIterator(streamData1.iterator(), onClose1, airbyteStream1)), airbyteStreamStatusConsumer);
    final Set<String> results = new HashSet<>();

    while (iterator.hasNext()) {
      results.add(iterator.next());
    }

    assertEquals(3, results.size());
    assertTrue(results.containsAll(streamData1));

    iterator.close();

    assertFalse(iterator.hasNext());
    verify(onClose1, times(1)).call();
    verify(airbyteStreamStatusConsumer, times(3)).accept(any());
  }

  @Test
  void errorConsumingFromIterator() {
    final LazyAutoCloseableIterator<String> childIterator = mock(LazyAutoCloseableIterator.class);
    lenient().when(childIterator.getAirbyteStream()).thenReturn(Optional.of(airbyteStream1));
    when(childIterator.hasNext()).thenThrow(new NullPointerException("test"));

    final AutoCloseableIterator<String> iterator = new ParallelCompositeIterator<>(List.of(
        AutoCloseableIterators.fromIterator(childIterator, onClose1, airbyteStream1)), airbyteStreamStatusConsumer);

    assertDoesNotThrow(() -> {
      iterator.hasNext();
      verify(airbyteStreamStatusConsumer, times(2)).accept(airbyteStreamStatusHolderArgumentCaptor.capture());
      assertEquals(AirbyteStreamStatus.INCOMPLETE,
          airbyteStreamStatusHolderArgumentCaptor.getAllValues().get(1).toTraceMessage().getStreamStatus().getStatus());
    });
  }

  @Test
  void noStatusWithoutStreamInformation() {
    final AutoCloseableIterator<String> childIterator = mock(AutoCloseableIterator.class);
    final AutoCloseableIterator<String> iterator = new ParallelCompositeIterator<>(List.of(childIterator), airbyteStreamStatusConsumer);

    assertDoesNotThrow(() -> {
      while (iterator.hasNext()) {
        iterator.next();
      }

      verify(airbyteStreamStatusConsumer, times(0)).accept(any());
    });
  }

  @Test
  void testAirbyteStreamEmptyOptional() {
    final ParallelCompositeIterator<String> iterator = new ParallelCompositeIterator<>(List.of(), airbyteStreamStatusConsumer);
    assertEquals(Optional.empty(), iterator.getAirbyteStream());
  }

}
