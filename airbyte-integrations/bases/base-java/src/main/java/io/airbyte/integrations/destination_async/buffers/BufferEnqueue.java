/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentMap;

/**
 * Represents the minimal interface over the underlying buffer queues required for enqueue
 * operations with the aim of minimizing lower-level queue access.
 */
public class BufferEnqueue {

  private final long initialQueueSizeBytes;
  private final RecordSizeEstimator recordSizeEstimator;

  private final GlobalMemoryManager memoryManager;
  private final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

  public BufferEnqueue(final GlobalMemoryManager memoryManager,
                       final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
    this(GlobalMemoryManager.BLOCK_SIZE_BYTES, memoryManager, buffers);
  }

  @VisibleForTesting
  public BufferEnqueue(final long initialQueueSizeBytes,
                       final GlobalMemoryManager memoryManager,
                       final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
    this.initialQueueSizeBytes = initialQueueSizeBytes;
    this.memoryManager = memoryManager;
    this.buffers = buffers;
    this.recordSizeEstimator = new RecordSizeEstimator();
  }

  /**
   * Buffer a record. Contains memory management logic to dynamically adjust queue size based via
   * {@link GlobalMemoryManager} accounting for incoming records.
   *
   * @param streamDescriptor stream to buffer record to
   * @param message to buffer
   */
  public void addRecord(final StreamDescriptor streamDescriptor, final AirbyteMessage message) {
    if (!buffers.containsKey(streamDescriptor)) {
      buffers.put(streamDescriptor, new MemoryBoundedLinkedBlockingQueue<>(memoryManager.requestMemory()));
    }

    // todo (cgardens) - handle estimating state message size.
    final long messageSize = message.getType() == AirbyteMessage.Type.RECORD ? recordSizeEstimator.getEstimatedByteSize(message.getRecord()) : 1024;

    final var queue = buffers.get(streamDescriptor);
    var addedToQueue = queue.offer(message, messageSize);

    // todo (cgardens) - what if the record being added is bigger than the block size?
    // if failed, try to increase memory and add to queue.
    while (!addedToQueue) {
      final var newlyAllocatedMemory = memoryManager.requestMemory();
      if (newlyAllocatedMemory > 0) {
        queue.addMaxMemory(newlyAllocatedMemory);
      }
      addedToQueue = queue.offer(message, messageSize);
    }
  }

}
