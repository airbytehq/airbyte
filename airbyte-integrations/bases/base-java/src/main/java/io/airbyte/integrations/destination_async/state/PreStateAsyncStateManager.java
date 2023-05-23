/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicLong;

// todo (cgardens) - hook it up to the memory manager.
public class PreStateAsyncStateManager {

  private final ConcurrentMap<Long, AtomicLong> stateIdToCounter;
  private final ConcurrentMap<StreamDescriptor, Long> streamToStateId;
  private long lastStateId = 0;

  public PreStateAsyncStateManager() {
    stateIdToCounter = new ConcurrentHashMap<>();
    streamToStateId = new ConcurrentHashMap<>();
  }

  public long getStateId(final StreamDescriptor streamDescriptor) {
    return getOrCreateInitialCounter(streamDescriptor);
  }

  // not threadsafe.
  private long getOrCreateInitialCounter(final StreamDescriptor streamDescriptor) {
    if (!streamToStateId.containsKey(streamDescriptor)) {
      streamToStateId.put(streamDescriptor, lastStateId++);
      stateIdToCounter.put(lastStateId, new AtomicLong());
    }
    return streamToStateId.get(streamDescriptor);
  }

  public void decrement(final long stateId) {

  }

  public PreStateOutput convert() {
    return new PreStateOutput(stateIdToCounter, streamToStateId, lastStateId);
  }

  record PreStateOutput(ConcurrentMap<Long, AtomicLong> stateIdToCounter,
                        ConcurrentMap<StreamDescriptor, Long> streamToStateId,
                        long lastStateId) {}

}
