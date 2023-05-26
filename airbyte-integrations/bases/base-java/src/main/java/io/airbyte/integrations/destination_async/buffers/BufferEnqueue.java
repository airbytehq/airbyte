/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.state.GlobalAsyncStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Represents the minimal interface over the underlying buffer queues required for enqueue
 * operations with the aim of minimizing lower-level queue access.
 */
public class BufferEnqueue {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferEnqueue.class);
  private final RecordSizeEstimator recordSizeEstimator;
  private final GlobalMemoryManager memoryManager;
  private final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers;
  private final GlobalAsyncStateManager stateManager;

  public BufferEnqueue(final GlobalMemoryManager memoryManager,
                       final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers,
                       final GlobalAsyncStateManager stateManager) {
    this.memoryManager = memoryManager;
    this.buffers = buffers;
    recordSizeEstimator = new RecordSizeEstimator();
    this.stateManager = stateManager;
  }

  /**
   * Buffer a record. Contains memory management logic to dynamically adjust queue size based via
   * {@link GlobalMemoryManager} accounting for incoming records.
   *
   * @param streamDescriptor stream to buffer record to
   * @param message to buffer
   */
  public void addRecord(final AirbyteMessage message) {
    if (message.getType() == Type.RECORD) {
      handleRecord(message);
    } else if (message.getType() == Type.STATE) {
      // todo (cgardens) - feed size into this method. depends on
      // https://github.com/airbytehq/airbyte/pull/26332
      stateManager.trackState(message, 1000L);
    }
  }

  private void handleRecord(final AirbyteMessage message) {
    final StreamDescriptor streamDescriptor = extractStateFromRecord(message);
    if (streamDescriptor != null && !buffers.containsKey(streamDescriptor)) {
      buffers.put(streamDescriptor, new StreamAwareQueue(memoryManager.requestMemory()));
    }
    // todo (cgardens) - i hate this thing. it's mostly useless.
    final long messageSize = recordSizeEstimator.getEstimatedByteSize(message.getRecord());
    final long stateId = stateManager.getStateIdAndIncrementCounter(streamDescriptor);

    final var queue = buffers.get(streamDescriptor);
    var addedToQueue = queue.offer(message, messageSize, stateId);

    while (!addedToQueue) {
      final var newlyAllocatedMemory = memoryManager.requestMemory();
      if (newlyAllocatedMemory > 0) {
        queue.addMaxMemory(newlyAllocatedMemory);
      }
      addedToQueue = queue.offer(message, messageSize, stateId);
    }
  }

  private static StreamDescriptor extractStateFromRecord(final AirbyteMessage message) {
    return new StreamDescriptor()
        .withNamespace(message.getRecord().getNamespace())
        .withName(message.getRecord().getStream());
  }

}
