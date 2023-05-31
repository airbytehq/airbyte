/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.HashSet;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Stream;

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
  private final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;
  private final ConcurrentMap<StreamDescriptor, ReentrantLock> bufferLocks;

  public BufferDequeue(final GlobalMemoryManager memoryManager,
                       final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
    this.memoryManager = memoryManager;
    this.buffers = buffers;
    bufferLocks = new ConcurrentHashMap<>();
  }

  /**
   * Primary dequeue method. Best-effort read a specified optimal memory size from the queue.
   *
   * @param streamDescriptor specific buffer to take from
   * @param optimalBytesToRead bytes to read, if possible
   * @return
   */
  public MemoryAwareMessageBatch take(final StreamDescriptor streamDescriptor, final long optimalBytesToRead) {
    final var queue = buffers.get(streamDescriptor);

    if (!bufferLocks.containsKey(streamDescriptor)) {
      bufferLocks.put(streamDescriptor, new ReentrantLock());
    }

    bufferLocks.get(streamDescriptor).lock();
    try {
      final AtomicLong bytesRead = new AtomicLong();

      final var s = Stream.generate(() -> {
        try {
          return queue.poll(20, TimeUnit.MILLISECONDS);
        } catch (final InterruptedException e) {
          throw new RuntimeException(e);
        }
      }).takeWhile(memoryItem -> {
        // if no new records after waiting, the stream is done.
        if (memoryItem == null) {
          return false;
        }

        // otherwise pull records until we hit the memory limit.
        final long newSize = memoryItem.size() + bytesRead.get();
        if (newSize <= optimalBytesToRead) {
          bytesRead.addAndGet(memoryItem.size());
          return true;
        } else {
          return false;
        }
      }).map(MemoryBoundedLinkedBlockingQueue.MemoryItem::item)
          .toList()
          .stream();

      queue.addMaxMemory(-bytesRead.get());

      return new MemoryAwareMessageBatch(s, bytesRead.get(), memoryManager);
    } finally {
      bufferLocks.get(streamDescriptor).unlock();
    }
  }

  /**
   * The following methods are provide metadata for buffer flushing calculations. Consumers are
   * expected to call {@link #getBufferedStreams()} to retrieve the currently buffered streams as a
   * handle to the remaining methods.
   */

  public Set<StreamDescriptor> getBufferedStreams() {
    return new HashSet<>(buffers.keySet());
  }

  public long getMaxQueueSizeBytes() {
    return memoryManager.getMaxMemoryBytes();
  }

  public long getTotalGlobalQueueSizeBytes() {
    return buffers.values().stream().map(MemoryBoundedLinkedBlockingQueue::getCurrentMemoryUsage).mapToLong(Long::longValue).sum();
  }

  public Optional<Long> getQueueSizeInRecords(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).map(buf -> Long.valueOf(buf.size()));
  }

  public Optional<Long> getQueueSizeBytes(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).map(MemoryBoundedLinkedBlockingQueue::getCurrentMemoryUsage);
  }

  public Optional<Instant> getTimeOfLastRecord(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).flatMap(MemoryBoundedLinkedBlockingQueue::getTimeOfLastMessage);
  }

  private Optional<MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> getBuffer(final StreamDescriptor streamDescriptor) {
    if (buffers.containsKey(streamDescriptor)) {
      return Optional.of(buffers.get(streamDescriptor));
    }
    return Optional.empty();
  }

}
