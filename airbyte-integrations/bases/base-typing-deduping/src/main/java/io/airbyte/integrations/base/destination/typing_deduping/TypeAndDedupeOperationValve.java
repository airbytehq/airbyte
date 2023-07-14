/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * A slightly more complicated way to keep track of when to perform type and dedupe operations per
 * stream
 */
public class TypeAndDedupeOperationValve extends ConcurrentHashMap<AirbyteStreamNameNamespacePair, Long> {

  private static final long TWO_MINUTES_MILLIS = 1000 * 60 * 2;

  private static final long FIVE_MINUTES_MILLIS = 1000 * 60 * 5;

  private static final long TEN_MINUTES_MILLIS = 1000 * 60 * 10;

  // 15 minutes is the maximum amount of time allowed between checkpoints as defined by
  // The Airbyte Protocol
  private static final long FIFTEEN_MINUTES_MILLIS = 1000 * 60 * 15;

  // New users of airbyte likely want to see data flowing into their tables as soon as possible
  // However, as their destination tables grow in size, typing and de-duping data becomes an expensive
  // operation
  // To strike a balance between showing data quickly and not slowing down the entire sync, we use an
  // increasing
  // interval based approach. This is not fancy, just hard coded intervals.
  private static final List<Long> typeAndDedupeIncreasingIntervals = List.of(
      TWO_MINUTES_MILLIS,
      FIVE_MINUTES_MILLIS,
      TEN_MINUTES_MILLIS,
      FIFTEEN_MINUTES_MILLIS);

  // Constantly getting the system time adds a bit of overhead, adding a minimum record count
  // To reduce calls for system time
  private static final int MINIMUM_RECORD_INTERVAL = 100;

  private static final Supplier<Long> SYSTEM_NOW = () -> System.currentTimeMillis();

  private ConcurrentHashMap<AirbyteStreamNameNamespacePair, Integer> incrementalIndex;

  private final Supplier<Long> nowness;
  private ConcurrentHashMap<AirbyteStreamNameNamespacePair, Long> recordCounts;

  public TypeAndDedupeOperationValve() {
    this(SYSTEM_NOW);
  }

  /**
   * This constructor is here because mocking System.currentTimeMillis() is a pain :(
   *
   * @param nownessSupplier Supplier which will return a long value representing now
   */
  public TypeAndDedupeOperationValve(Supplier<Long> nownessSupplier) {
    super();
    incrementalIndex = new ConcurrentHashMap<>();
    recordCounts = new ConcurrentHashMap<>();
    this.nowness = nownessSupplier;
  }

  @Override
  public Long put(final AirbyteStreamNameNamespacePair key, final Long value) {
    if (!incrementalIndex.containsKey(key)) {
      incrementalIndex.put(key, 0);
    }
    if (!recordCounts.containsKey(key)) {
      recordCounts.put(key, 1l);
    }
    return super.put(key, value);

  }

  /**
   * Adds a stream specific timestamp to track type and dedupe operations
   *
   * @param key the AirbyteStreamNameNamespacePair to track
   */
  public void addStream(final AirbyteStreamNameNamespacePair key) {
    put(key, nowness.get());
  }

  /**
   * Whether we should type and dedupe at this point in time for this particular stream.
   *
   * @param key the stream in question
   * @return a boolean indicating whether we have crossed the interval threshold for typing and
   *         deduping.
   */
  public boolean readyToTypeAndDedupeWithAdditionalRecord(final AirbyteStreamNameNamespacePair key) {
    return false;
    // if (!containsKey(key)) {
    // return false;
    // }
    // recordCounts.put(key, recordCounts.get(key) + 1);
    // if (recordCounts.get(key) % MINIMUM_RECORD_INTERVAL == 0) {
    // return nowness.get() - get(key) >
    // typeAndDedupeIncreasingIntervals.get(incrementalIndex.get(key));
    // }
    // return false;
  }

  /**
   * Increment the interval at which typing and deduping should occur for the stream, max out at last
   * index of {@link TypeAndDedupeOperationValve#typeAndDedupeIncreasingIntervals}
   *
   * @param key the stream to increment the interval of
   * @return the index of the typing and deduping interval associated with this stream
   */
  public int incrementInterval(final AirbyteStreamNameNamespacePair key) {
    if (incrementalIndex.get(key) < typeAndDedupeIncreasingIntervals.size() - 1) {
      incrementalIndex.put(key, incrementalIndex.get(key) + 1);
    }
    return incrementalIndex.get(key);
  }

  /**
   * Meant to be called after
   * {@link TypeAndDedupeOperationValve#readyToTypeAndDedupeWithAdditionalRecord(AirbyteStreamNameNamespacePair)}
   * will set a streams last operation to the current time and increase its index reference in
   * {@link TypeAndDedupeOperationValve#typeAndDedupeIncreasingIntervals}
   *
   * @param key the stream to update
   */
  public void updateTimeAndIncreaseInterval(final AirbyteStreamNameNamespacePair key) {
    put(key, nowness.get());
    incrementInterval(key);
  }

  /**
   * Get the current interval for the stream
   *
   * @param key the stream in question
   * @return a long value representing the length of the interval milliseconds
   */
  public Long getIncrementInterval(final AirbyteStreamNameNamespacePair key) {
    return typeAndDedupeIncreasingIntervals.get(incrementalIndex.get(key));
  }

  /**
   * Get the current record count per stream
   *
   * @param key the stream in question
   * @return the recrod count
   */
  public Long getRecordCount(final AirbyteStreamNameNamespacePair key) {
    return recordCounts.get(key);
  }

}
