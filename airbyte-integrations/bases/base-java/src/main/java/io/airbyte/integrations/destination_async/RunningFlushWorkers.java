/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class RunningFlushWorkers {

  private final ConcurrentHashMap<StreamDescriptor, AtomicInteger> streamToInProgressWorkers;

  public RunningFlushWorkers() {
    streamToInProgressWorkers = new ConcurrentHashMap<>();
  }

  public void trackFlushWorker(final StreamDescriptor stream) {
    streamToInProgressWorkers.computeIfAbsent(stream, ignored -> new AtomicInteger(0)).incrementAndGet();
  }

  public void completeFlushWorker(final StreamDescriptor stream) {
    Preconditions.checkState(streamToInProgressWorkers.containsKey(stream), "Cannot complete flush worker for stream that has not started.");
    streamToInProgressWorkers.get(stream).decrementAndGet();
  }

  public int getNumFlushWorkers(final StreamDescriptor stream) {
    return streamToInProgressWorkers.getOrDefault(stream, new AtomicInteger(0)).get();
  }

}
