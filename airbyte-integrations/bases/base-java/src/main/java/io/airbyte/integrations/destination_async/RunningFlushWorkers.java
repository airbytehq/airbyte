/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Track the number of flush workers that are currently running for a given stream.
 */
public class RunningFlushWorkers {

  private final ConcurrentHashMap<StreamDescriptor, AtomicInteger> streamToInProgressWorkers;

  public RunningFlushWorkers() {
    streamToInProgressWorkers = new ConcurrentHashMap<>();
  }

  /**
   * Call this when a worker starts flushing a stream.
   *
   * @param stream the stream that is being flushed
   */
  public void trackFlushWorker(final StreamDescriptor stream) {
    streamToInProgressWorkers.computeIfAbsent(stream, ignored -> new AtomicInteger(0)).incrementAndGet();
  }

  /**
   * Call this when a worker completes flushing a stream.
   *
   * @param stream the stream that was flushed
   */
  public void completeFlushWorker(final StreamDescriptor stream) {
    Preconditions.checkState(streamToInProgressWorkers.containsKey(stream), "Cannot complete flush worker for stream that has not started.");
    streamToInProgressWorkers.get(stream).decrementAndGet();
  }

  /**
   * Get the number of flush workers that are currently running for a given stream.
   *
   * @param stream the stream to check
   * @return the number of flush workers that are currently running for the given stream
   */
  public int getNumFlushWorkers(final StreamDescriptor stream) {
    return streamToInProgressWorkers.getOrDefault(stream, new AtomicInteger(0)).get();
  }

}
