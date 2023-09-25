/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.buffers.MemoryBoundedLinkedBlockingQueue.MemoryItem;
import io.airbyte.integrations.destination_async.buffers.StreamAwareQueue.MessageWithMeta;
import io.airbyte.integrations.destination_async.state.GlobalAsyncStateManager;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Represents the minimal interface over the underlying buffer queues required for dequeue
 * operations with the aim of minimizing lower-level queue access.
 * <p>
 * Aside from {@link #take(StreamDescriptor, long)}, all public methods in this class represents
 * queue metadata required to determine buffer flushing.
 */
// todo (cgardens) - make all the metadata methods more efficient.
public class BufferDequeue {

  private final GlobalMemoryManager memoryManager;
  private final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers;
  private final GlobalAsyncStateManager stateManager;
  private final ConcurrentMap<StreamDescriptor, ReentrantLock> bufferLocks;

  public BufferDequeue(final GlobalMemoryManager memoryManager,
                       final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers,
                       final GlobalAsyncStateManager stateManager) {
    this.memoryManager = memoryManager;
    this.buffers = buffers;
    this.stateManager = stateManager;
    bufferLocks = new ConcurrentHashMap<>();
  }

  /**
   * Primary dequeue method. Reads from queue up to optimalBytesToRead OR until the queue is empty.
   *
   * @param streamDescriptor specific buffer to take from
   * @param optimalBytesToRead bytes to read, if possible
   * @return autocloseable batch object, that frees memory.
   */
  public MemoryAwareMessageBatch take(final StreamDescriptor streamDescriptor, final long optimalBytesToRead) {
    final var queue = buffers.get(streamDescriptor);

    if (!bufferLocks.containsKey(streamDescriptor)) {
      bufferLocks.put(streamDescriptor, new ReentrantLock());
    }

    bufferLocks.get(streamDescriptor).lock();
    try {
      final AtomicLong bytesRead = new AtomicLong();

      final List<MessageWithMeta> output = new LinkedList<>();
      while (queue.size() > 0) {
        final MemoryItem<MessageWithMeta> memoryItem = queue.peek().orElseThrow();

        // otherwise pull records until we hit the memory limit.
        final long newSize = memoryItem.size() + bytesRead.get();
        if (newSize <= optimalBytesToRead) {
          bytesRead.addAndGet(memoryItem.size());
          output.add(queue.poll().item());
        } else {
          break;
        }
      }

      queue.addMaxMemory(-bytesRead.get());

      return new MemoryAwareMessageBatch(
          output,
          bytesRead.get(),
          memoryManager,
          stateManager);
    } finally {
      bufferLocks.get(streamDescriptor).unlock();
    }
  }

  /**
   * The following methods are provide metadata for buffer flushing calculations. Consumers are
   * expected to call it to retrieve the currently buffered streams as a handle to the remaining
   * methods.
   */
  public Set<StreamDescriptor> getBufferedStreams() {
    return new HashSet<>(buffers.keySet());
  }

  public long getMaxQueueSizeBytes() {
    return memoryManager.getMaxMemoryBytes();
  }

  public long getTotalGlobalQueueSizeBytes() {
    return buffers.values().stream().map(StreamAwareQueue::getCurrentMemoryUsage).mapToLong(Long::longValue).sum();
  }

  public Optional<Long> getQueueSizeInRecords(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).map(buf -> Long.valueOf(buf.size()));
  }

  public Optional<Long> getQueueSizeBytes(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).map(StreamAwareQueue::getCurrentMemoryUsage);
  }

  public Optional<Instant> getTimeOfLastRecord(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).flatMap(StreamAwareQueue::getTimeOfLastMessage);
  }

  private Optional<StreamAwareQueue> getBuffer(final StreamDescriptor streamDescriptor) {
    if (buffers.containsKey(streamDescriptor)) {
      return Optional.of(buffers.get(streamDescriptor));
    }
    return Optional.empty();
  }

}
