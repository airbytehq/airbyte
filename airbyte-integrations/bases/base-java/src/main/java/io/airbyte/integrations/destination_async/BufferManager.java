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
  // public static final long TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES = 4L * 1024 * 1024 * 1024; // 4 GB for
  // now
  public static final long BLOCK_SIZE_BYTES = 10 * 1024 * 1024;
  public static final long INITIAL_QUEUE_SIZE_BYTES = BLOCK_SIZE_BYTES;
  public static final long MAX_CONCURRENT_QUEUES = 10L;
  public static final long QUEUE_FLUSH_THRESHOLD_BYTES = 40 * 1024 * 1024; // 40MB

  private final ConcurrentMap<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;
  private final BufferManagerEnqueue bufferManagerEnqueue;
  private final BufferManagerDequeue bufferManagerDequeue;
  private final GlobalMemoryManager memoryManager;
  private final ScheduledExecutorService debugLoop = Executors.newSingleThreadScheduledExecutor();

  public BufferManager() {
    log.info("BufferManager max memory limit: {}", TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES);
    memoryManager = new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES);
    buffers = new ConcurrentHashMap<>();
    bufferManagerEnqueue = new BufferManagerEnqueue(memoryManager, buffers);
    bufferManagerDequeue = new BufferManagerDequeue(memoryManager, buffers);
    debugLoop.scheduleAtFixedRate(this::printQueueInfo, 0, 5, TimeUnit.SECONDS);
  }

  public BufferManagerEnqueue getBufferManagerEnqueue() {
    return bufferManagerEnqueue;
  }

  public BufferManagerDequeue getBufferManagerDequeue() {
    return bufferManagerDequeue;
  }

  /**
   * Closing a queue will flush all items from it. For this reason, this method needs to be called
   * after {@link UploadWorkers#close()}. This allows the upload workers to make sure all items in the
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
        buffers.put(streamDescriptor, new MemoryBoundedLinkedBlockingQueue<>(memoryManager.requestMemory()));
      }

      // todo (cgardens) - handle estimating state message size.
      final long messageSize = message.getType() == AirbyteMessage.Type.RECORD ? recordSizeEstimator.getEstimatedByteSize(message.getRecord()) : 1024;

      final var queue = buffers.get(streamDescriptor);
      var addedToQueue = queue.offer(message, messageSize);

      // todo (cgardens) - what if the record being added is bigger than the bock size?
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
          if (newSize <= bytesToRead) {
            bytesRead.addAndGet(memoryItem.size());
            return true;
          } else {
            return false;
          }
        }).map(MemoryItem::item)
            .toList()
            .stream();

        queue.addMaxMemory(-bytesRead.get());

        log.info("Setting batch memory to {}", bytesRead.get());
        return new Batch(s, bytesRead.get(), memoryManager);
      } finally {
        bufferLocks.get(streamDescriptor).unlock();
      }
    }

    public static class Batch implements AutoCloseable {

      private final Stream<AirbyteMessage> batch;
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

      public long getSizeInBytes() {
        return sizeInBytes;
      }

      @Override
      public void close() throws Exception {
        memoryManager.free(sizeInBytes);
      }

    }

  }

  @Slf4j
  static class GlobalMemoryManager {

    private static final long BLOCK_SIZE_BYTES = 10 * 1024 * 1024; // 10MB
    private final long maxMemoryBytes;

    private final AtomicLong currentMemoryBytes = new AtomicLong(0);

    public GlobalMemoryManager(final long maxMemoryBytes) {
      this.maxMemoryBytes = maxMemoryBytes;
    }

    public long getMaxMemoryBytes() {
      return maxMemoryBytes;
    }

    public long getCurrentMemoryBytes() {
      return currentMemoryBytes.get();
    }

    public synchronized long requestMemory() {
      if (currentMemoryBytes.get() >= maxMemoryBytes) {
        return 0L;
      }

      final var freeMem = maxMemoryBytes - currentMemoryBytes.get();
      // Never allocate more than free memory size.
      final var toAllocateBytes = Math.min(freeMem, BLOCK_SIZE_BYTES);
      currentMemoryBytes.addAndGet(toAllocateBytes);

      return toAllocateBytes;
    }

    public void free(final long bytes) {
      log.info("Freeing {} bytes..", bytes);

      currentMemoryBytes.addAndGet(-bytes);

      if (currentMemoryBytes.get() < 0) {
        log.warn("Freed more memory than allocated. This should never happen. Please report this bug.");
      }
    }

  }

}
