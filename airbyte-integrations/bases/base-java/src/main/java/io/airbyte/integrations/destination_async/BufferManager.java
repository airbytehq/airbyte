/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination_async.MemoryBoundedLinkedBlockingQueue.MemoryItem;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

@Slf4j
public class BufferManager {

  public static final long TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES = (long) (Runtime.getRuntime().maxMemory() * 0.8);
  public static final long BLOCK_SIZE_BYTES = 10 * 1024 * 1024;
  public static final long INITIAL_QUEUE_SIZE_BYTES = BLOCK_SIZE_BYTES;
  public static final long MAX_CONCURRENT_QUEUES = 10L;
  public static final long QUEUE_FLUSH_THRESHOLD = 10 * 1024 * 1024; // 10MB

  private final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;
  private final BufferManagerEnqueue bufferManagerEnqueue;
  private final BufferManagerDequeue bufferManagerDequeue;
  private final GlobalMemoryManager memoryManager;
  private final ScheduledExecutorService debugLoop = Executors.newSingleThreadScheduledExecutor();

  public BufferManager() {
    memoryManager = new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES);
    buffers = new ConcurrentHashMap<>();
    bufferManagerEnqueue = new BufferManagerEnqueue(memoryManager, buffers);
    bufferManagerDequeue = new BufferManagerDequeue(memoryManager, buffers);
    debugLoop.scheduleAtFixedRate(this::printQueueInfo, 0, 10, TimeUnit.SECONDS);
  }

  public BufferManagerEnqueue getBufferManagerEnqueue() {
    return bufferManagerEnqueue;
  }

  public BufferManagerDequeue getBufferManagerDequeue() {
    return bufferManagerDequeue;
  }

  /**
   * Closing a queue will flush all items from it. For this reason, this method needs to be called
   * after {@link FlushWorkers#close()}. This allows the upload workers to make sure all items in the
   * queue has been flushed.
   */
  public void close() throws Exception {
    debugLoop.shutdownNow();
    log.info("Buffers cleared..");
  }

  private void printQueueInfo() {
    final var queueInfo = new StringBuilder().append("QUEUE INFO").append(System.lineSeparator());

    queueInfo
        .append(String.format("  Global Mem Manager -- max: %s, allocated: %s",
            FileUtils.byteCountToDisplaySize(memoryManager.getMaxMemoryBytes()),
            FileUtils.byteCountToDisplaySize(memoryManager.getCurrentMemoryBytes())))
        .append(System.lineSeparator());

    for (final var entry : buffers.entrySet()) {
      final var queue = entry.getValue();
      queueInfo.append(
          String.format("  Queue name: %s, num records: %d, num bytes: %s",
              entry.getKey().getName(), queue.size(), FileUtils.byteCountToDisplaySize(queue.getCurrentMemoryUsage())))
          .append(System.lineSeparator());
    }
    log.info(queueInfo.toString());
  }

  public static class BufferManagerEnqueue {

    private final RecordSizeEstimator recordSizeEstimator;

    private final GlobalMemoryManager memoryManager;
    private final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

    public BufferManagerEnqueue(final GlobalMemoryManager memoryManager,
                                final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
      this.memoryManager = memoryManager;
      this.buffers = buffers;
      recordSizeEstimator = new RecordSizeEstimator();
    }

    public void addRecord(final StreamDescriptor streamDescriptor, final AirbyteMessage message) {
      if (!buffers.containsKey(streamDescriptor)) {
        buffers.put(streamDescriptor, new MemoryBoundedLinkedBlockingQueue<>(INITIAL_QUEUE_SIZE_BYTES));
      }

      // todo (cgardens) - handle estimating state message size.
      final long messageSize = message.getType() == AirbyteMessage.Type.RECORD ? recordSizeEstimator.getEstimatedByteSize(message.getRecord()) : 1024;

      final var queue = buffers.get(streamDescriptor);
      var addedToQueue = queue.offer(message, messageSize);

      // todo (cgardens) - what if the record being added is bigger than the bock size?
      // if failed, try to increase memory and add to queue.
      while (!addedToQueue) {
        final var freeMem = memoryManager.requestMemory();
        if (freeMem > 0) {
          queue.setMaxMemoryUsage(queue.getMaxMemoryUsage() + freeMem);
        }
        addedToQueue = queue.offer(message, messageSize);
      }
    }

  }

  // todo (cgardens) - make all the metadata methods more efficient.
  static class BufferManagerDequeue {

    private final GlobalMemoryManager memoryManager;
    private final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;
    private final ConcurrentMap<StreamDescriptor, ReentrantLock> bufferLocks;

    public BufferManagerDequeue(final GlobalMemoryManager memoryManager,
                                final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
      this.memoryManager = memoryManager;
      this.buffers = buffers;
      bufferLocks = new ConcurrentHashMap<>();
    }

    public Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> getBuffers() {
      return new HashMap<>(buffers);
    }

    private MemoryBoundedLinkedBlockingQueue<AirbyteMessage> getBuffer(final StreamDescriptor streamDescriptor) {
      return buffers.get(streamDescriptor);
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
        }).map(MemoryItem::item)
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

    public static class Batch implements AutoCloseable {

      private Stream<AirbyteMessage> batch;
      private final long sizeInBytes;
      private final GlobalMemoryManager memoryManager;

      public Batch(final Stream<AirbyteMessage> batch, final long sizeInBytes, final GlobalMemoryManager memoryManager) {
        this.batch = batch;
        this.sizeInBytes = sizeInBytes;
        this.memoryManager = memoryManager;
      }

      public Stream<AirbyteMessage> getData() {
        return batch;
      }

      @Override
      public void close() throws Exception {
        batch = null;
        memoryManager.free(sizeInBytes);
      }

    }

  }

}
