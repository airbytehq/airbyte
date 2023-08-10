/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;
import java.util.stream.IntStream;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class TypeAndDedupeOperationValveTest {

  private static final AirbyteStreamNameNamespacePair STREAM_A = new AirbyteStreamNameNamespacePair("a", "a");
  private static final AirbyteStreamNameNamespacePair STREAM_B = new AirbyteStreamNameNamespacePair("b", "b");
  private static final Supplier<Long> ALWAYS_ZERO = () -> 0l;

  private Supplier<Long> minuteUpdates;

  @BeforeEach
  public void setup() {
    AtomicLong start = new AtomicLong(0);
    minuteUpdates = () -> start.getAndUpdate(l -> l + (60 * 1000));
  }

  private void elapseTime(Supplier<Long> timing, int iterations) {
    IntStream.range(0, iterations).forEach(__ -> {
      timing.get();
    });
  }

  @Test
  public void testAddStream() {
    final var valve = new TypeAndDedupeOperationValve(ALWAYS_ZERO);
    valve.addStream(STREAM_A);
    Assertions.assertEquals(-1, valve.getIncrementInterval(STREAM_A));
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
    Assertions.assertEquals(valve.get(STREAM_A), 0l);
  }

  @Test
  public void testReadyToTypeAndDedupe() {
    final var valve = new TypeAndDedupeOperationValve(minuteUpdates);
    // method call increments time
    valve.addStream(STREAM_A);
    elapseTime(minuteUpdates, 1);
    // method call increments time
    valve.addStream(STREAM_B);
    // method call increments time
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
    elapseTime(minuteUpdates, 1);
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_B));
    valve.updateTimeAndIncreaseInterval(STREAM_A);
    Assertions.assertEquals(1000 * 60 * 15,
        valve.getIncrementInterval(STREAM_A));
    // method call increments time
    Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A));
    // More than enough time has passed now
    elapseTime(minuteUpdates, 15);
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
  }

  @Test
  public void testIncrementInterval() {
    final var valve = new TypeAndDedupeOperationValve(ALWAYS_ZERO);
    valve.addStream(STREAM_A);
    IntStream.rangeClosed(1, 4).forEach(i -> {
      final var index = valve.incrementInterval(STREAM_A);
      Assertions.assertEquals(i, index);
    });
    Assertions.assertEquals(4, valve.incrementInterval(STREAM_A));
    // Twice to be sure
    Assertions.assertEquals(4, valve.incrementInterval(STREAM_A));
  }

  @Test
  public void testUpdateTimeAndIncreaseInterval() {
    final var valve = new TypeAndDedupeOperationValve(minuteUpdates);
    valve.addStream(STREAM_A);
    IntStream.range(0, 1).forEach(__ -> Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A))); // start ready to T&D
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
    valve.updateTimeAndIncreaseInterval(STREAM_A);
    IntStream.range(0, 15).forEach(__ -> Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A)));
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
    valve.updateTimeAndIncreaseInterval(STREAM_A);
    IntStream.range(0, 60).forEach(__ -> Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A)));
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
    valve.updateTimeAndIncreaseInterval(STREAM_A);
    IntStream.range(0, 120).forEach(__ -> Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A)));
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
    valve.updateTimeAndIncreaseInterval(STREAM_A);
    IntStream.range(0, 240).forEach(__ -> Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A)));
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
    valve.updateTimeAndIncreaseInterval(STREAM_A);
    IntStream.range(0, 240).forEach(__ -> Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A)));
    Assertions.assertTrue(valve.readyToTypeAndDedupe(STREAM_A));
  }

}
