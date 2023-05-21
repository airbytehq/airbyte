/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
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
 * metadata required to determine buffer flushing.
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

  public Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> getBuffers() {
    return new HashMap<>(buffers);
  }

  public long getTotalGlobalQueueSizeBytes() {
    return buffers.values().stream().map(MemoryBoundedLinkedBlockingQueue::getCurrentMemoryUsage).mapToLong(Long::longValue).sum();
  }

  public long getQueueSizeInRecords(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).size();
  }

  public long getQueueSizeBytes(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).getCurrentMemoryUsage();
  }

  public Optional<Instant> getTimeOfLastRecord(final StreamDescriptor streamDescriptor) {
    return getBuffer(streamDescriptor).getTimeOfLastMessage();
  }

  public Batch take(final StreamDescriptor streamDescriptor, final long bytesToRead) {
    final var queue = buffers.get(streamDescriptor);

    if (!bufferLocks.containsKey(streamDescriptor)) {
      bufferLocks.put(streamDescriptor, new ReentrantLock());
    }

    bufferLocks.get(streamDescriptor).lock();
    try {
      final AtomicLong bytesRead = new AtomicLong();

      final var s = Stream.generate(() -> {
        try {
          return queue.poll(5, TimeUnit.MILLISECONDS);
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
        if (newSize <= bytesToRead) {
          bytesRead.addAndGet(memoryItem.size());
          return true;
        } else {
          return false;
        }
      }).map(MemoryBoundedLinkedBlockingQueue.MemoryItem::item)
          .toList()
          .stream();

      // todo (cgardens) - possible race where in between pulling records and new records going in that we
      // reset the limit to be lower than number of bytes already in the queue. probably not a big deal.
      queue.setMaxMemoryUsage(queue.getMaxMemoryUsage() - bytesRead.get());

      return new Batch(s, bytesRead.get(), memoryManager);
    } finally {
      bufferLocks.get(streamDescriptor).unlock();
    }
  }

  private MemoryBoundedLinkedBlockingQueue<AirbyteMessage> getBuffer(final StreamDescriptor streamDescriptor) {
    return buffers.get(streamDescriptor);
  }

}
