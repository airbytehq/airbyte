/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import static java.lang.Thread.sleep;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.state.GlobalAsyncStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentMap;

/**
 * Represents the minimal interface over the underlying buffer queues required for enqueue
 * operations with the aim of minimizing lower-level queue access.
 */
public class BufferEnqueue {

  private final GlobalMemoryManager memoryManager;
  private final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers;
  private final GlobalAsyncStateManager stateManager;

  public BufferEnqueue(final GlobalMemoryManager memoryManager,
                       final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers,
                       final GlobalAsyncStateManager stateManager) {
    this.memoryManager = memoryManager;
    this.buffers = buffers;
    this.stateManager = stateManager;
  }

  /**
   * Buffer a record. Contains memory management logic to dynamically adjust queue size based via
   * {@link GlobalMemoryManager} accounting for incoming records.
   *
   * @param message to buffer
   * @param sizeInBytes
   */
  public void addRecord(final PartialAirbyteMessage message, final Integer sizeInBytes) {
    if (message.getType() == Type.RECORD) {
      handleRecord(message, sizeInBytes);
    } else if (message.getType() == Type.STATE) {
      stateManager.trackState(message, sizeInBytes);
    }
  }

  private void handleRecord(final PartialAirbyteMessage message, final Integer sizeInBytes) {
    final StreamDescriptor streamDescriptor = extractStateFromRecord(message);
    if (streamDescriptor != null && !buffers.containsKey(streamDescriptor)) {
      buffers.put(streamDescriptor, new StreamAwareQueue(memoryManager.requestMemory()));
    }
    final long stateId = stateManager.getStateIdAndIncrementCounter(streamDescriptor);

    final var queue = buffers.get(streamDescriptor);
    var addedToQueue = queue.offer(message, sizeInBytes, stateId);

    int i = 0;
    while (!addedToQueue) {
      final var newlyAllocatedMemory = memoryManager.requestMemory();
      if (newlyAllocatedMemory > 0) {
        queue.addMaxMemory(newlyAllocatedMemory);
      }
      addedToQueue = queue.offer(message, sizeInBytes, stateId);
      i++;
      if (i > 5) {
        try {
          sleep(500);
        } catch (final InterruptedException e) {
          throw new RuntimeException(e);
        }
      }
    }
  }

  private static StreamDescriptor extractStateFromRecord(final PartialAirbyteMessage message) {
    return new StreamDescriptor()
        .withNamespace(message.getRecord().getNamespace())
        .withName(message.getRecord().getStream());
  }

}
