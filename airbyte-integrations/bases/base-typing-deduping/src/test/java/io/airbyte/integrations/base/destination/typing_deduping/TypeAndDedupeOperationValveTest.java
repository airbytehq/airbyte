/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public class TypeAndDedupeOperationValveTest {
  /*
   * private static final AirbyteStreamNameNamespacePair STREAM_A = new
   * AirbyteStreamNameNamespacePair("a", "a"); private static final AirbyteStreamNameNamespacePair
   * STREAM_B = new AirbyteStreamNameNamespacePair("b", "b");
   *
   * private static final Supplier<Long> ALWAYS_ZERO = () -> 0l;
   *
   * private Supplier<Long> minuteUpdates;
   *
   * @BeforeEach public void setup() { AtomicLong start = new AtomicLong(0); minuteUpdates = () ->
   * start.getAndUpdate(l -> l + (60 * 1000)); }
   *
   * private void elapseTime(Supplier<Long> timing, int iterations) { IntStream.range(0,
   * iterations).forEach(__ -> { timing.get(); }); }
   *
   * @Test public void testAddStream() { final var valve = new
   * TypeAndDedupeOperationValve(ALWAYS_ZERO); valve.addStream(STREAM_A); Assertions.assertEquals(1l,
   * valve.getRecordCount(STREAM_A)); Assertions.assertEquals(1000 * 60 * 2,
   * valve.getIncrementInterval(STREAM_A));
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A));
   * Assertions.assertEquals(valve.get(STREAM_A), 0l); }
   *
   * @Test public void testReadyToTypeAndDedupe() { final var valve = new
   * TypeAndDedupeOperationValve(minuteUpdates); // method call increments time
   * valve.addStream(STREAM_A); IntStream.range(0, 98).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)));
   * elapseTime(minuteUpdates, 1); // method call increments time valve.addStream(STREAM_B); // method
   * call increments time
   * Assertions.assertTrue(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A));
   * IntStream.range(0, 98).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_B)));
   * elapseTime(minuteUpdates, 1);
   * Assertions.assertTrue(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_B));
   * valve.updateTimeAndIncreaseInterval(STREAM_A); Assertions.assertEquals(1000 * 60 * 5,
   * valve.getIncrementInterval(STREAM_A)); IntStream.range(0, 99).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)));
   * Assertions.assertEquals(199, valve.getRecordCount(STREAM_A)); // method call increments time //
   * This puts it at 200 records, which should then check to see if enough time has passed // but only
   * one minute has passed
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A));
   * elapseTime(minuteUpdates, 5); IntStream.range(0, 99).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)));
   * Assertions.assertEquals(299, valve.getRecordCount(STREAM_A)); // More than enough time has passed
   * now and this will be the 300th record
   * Assertions.assertTrue(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)); }
   *
   * @Test public void testIncrementInterval() { final var valve = new
   * TypeAndDedupeOperationValve(ALWAYS_ZERO); valve.addStream(STREAM_A); IntStream.rangeClosed(1,
   * 3).forEach(i -> { final var index = valve.incrementInterval(STREAM_A); Assertions.assertEquals(i,
   * index); }); Assertions.assertEquals(3, valve.incrementInterval(STREAM_A)); // Twice to be sure
   * Assertions.assertEquals(3, valve.incrementInterval(STREAM_A)); }
   *
   * @Test public void testUpdateTimeAndIncreaseInterval() { final var valve = new
   * TypeAndDedupeOperationValve(minuteUpdates); valve.addStream(STREAM_A); // 2 minutes
   * IntStream.range(0, 98).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)));
   * elapseTime(minuteUpdates, 2);
   * Assertions.assertTrue(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A));
   * valve.updateTimeAndIncreaseInterval(STREAM_A); // 5 minutes IntStream.range(0, 99).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)));
   * elapseTime(minuteUpdates, 5);
   * Assertions.assertTrue(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A));
   * valve.updateTimeAndIncreaseInterval(STREAM_A); // 10 minutes IntStream.range(0, 99).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)));
   * elapseTime(minuteUpdates, 10);
   * Assertions.assertTrue(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A));
   * valve.updateTimeAndIncreaseInterval(STREAM_A); // 15 minutes IntStream.range(0, 99).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)));
   * elapseTime(minuteUpdates, 15);
   * Assertions.assertTrue(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A));
   * valve.updateTimeAndIncreaseInterval(STREAM_A); // 15 minutes again IntStream.range(0,
   * 99).forEach(__ ->
   * Assertions.assertFalse(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)));
   * elapseTime(minuteUpdates, 15);
   * Assertions.assertTrue(valve.readyToTypeAndDedupeWithAdditionalRecord(STREAM_A)); }
   */
}
