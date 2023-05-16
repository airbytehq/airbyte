/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.*;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class BufferManager implements AutoCloseable {

  public static final long TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES = (long) (Runtime.getRuntime().maxMemory() * 0.8);
  public static final long BLOCK_SIZE_BYTES = 10 * 1024 * 1024;
  public static final long INITIAL_QUEUE_SIZE_BYTES =  BLOCK_SIZE_BYTES;
  public static final long MAX_CONCURRENT_QUEUES = 10L;
  public static final long MAX_QUEUE_SIZE_BYTES = TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES / MAX_CONCURRENT_QUEUES;

  Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

  BufferManagerEnqueue bufferManagerEnqueue;
  BufferManagerDequeue bufferManagerDequeue;

  public BufferManager() {
    buffers = new HashMap<>();
    var memoryManager = new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES);
    bufferManagerEnqueue = new BufferManagerEnqueue(memoryManager, buffers);
    bufferManagerDequeue = new BufferManagerDequeue(memoryManager, buffers);
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
  @Override
  public void close() throws Exception {
    buffers.forEach(((streamDescriptor, queue) -> queue.clear()));
    log.info("Buffers cleared..");
  }

  public static class BufferManagerEnqueue {

    private final RecordSizeEstimator recordSizeEstimator;

    private final GlobalMemoryManager memoryManager;
    private final Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

    public BufferManagerEnqueue(final GlobalMemoryManager memoryManager, final Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
      this.memoryManager = memoryManager;
      this.buffers = buffers;
      recordSizeEstimator = new RecordSizeEstimator();
    }

    public void addRecord(final StreamDescriptor streamDescriptor, final AirbyteMessage message) {
      // todo (cgardens) - share the total memory across multiple queues.
      final long availableMemory = (long) (Runtime.getRuntime().maxMemory() * 0.8);
      log.info("available memory: " + availableMemory);

      // todo (cgardens) - replace this with fancy logic to make sure we don't oom.
      if (!buffers.containsKey(streamDescriptor)) {
        buffers.put(streamDescriptor, new MemoryBoundedLinkedBlockingQueue<>(INITIAL_QUEUE_SIZE_BYTES));
      }

      // todo (cgardens) - handle estimating state message size.
      final long messageSize = message.getType() == AirbyteMessage.Type.RECORD ? recordSizeEstimator.getEstimatedByteSize(message.getRecord()) : 1024;
      final var queue = buffers.get(streamDescriptor);
      var addedToQueue = queue.offer(message, messageSize);

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
    private final Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

    public BufferManagerDequeue(final GlobalMemoryManager memoryManager, final Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
      this.memoryManager = memoryManager;
      this.buffers = buffers;
    }

    public Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> getBuffers() {
      return new HashMap<>(buffers);
    }

    public MemoryBoundedLinkedBlockingQueue<AirbyteMessage> getBuffer(final StreamDescriptor streamDescriptor) {
      return buffers.get(streamDescriptor);
    }

    public long getTotalGlobalQueueSizeInMb() {
      return buffers.values().stream().map(MemoryBoundedLinkedBlockingQueue::getCurrentMemoryUsage).mapToLong(Long::longValue).sum();
    }

    public long getQueueSizeInMb(final StreamDescriptor streamDescriptor) {
      return getBuffer(streamDescriptor).getCurrentMemoryUsage();
    }

    public Optional<Instant> getTimeOfLastRecord(final StreamDescriptor streamDescriptor) {
      return getBuffer(streamDescriptor).getTimeOfLastMessage();
    }

    public Batch take(final StreamDescriptor streamDescriptor, long bytesToRead) {
      var queue = buffers.get(streamDescriptor);
      return new Batch(List.of());
    }

    class Batch implements AutoCloseable {
      private long memUsageBytes = 1000;
      private GlobalMemoryManager memoryManager;
      List<AirbyteMessage> batch;

      Batch(final List<AirbyteMessage> batch) {
        this.batch = batch;
      }

      @Override
      public void close() throws Exception {
        memoryManager.free(memUsageBytes);
      }
    }

  }

  static class GlobalMemoryManager {
    public static final long BLOCK_SIZE_BYTES = 10 * 1024 * 1024;
    private long currentMemoryBytes = 0L;
    private final long maxMemoryBytes;

    // buffers

    public GlobalMemoryManager(final long maxMemoryBytes) {
      this.maxMemoryBytes = maxMemoryBytes;
    }

    public synchronized long requestMemory() {
      if (currentMemoryBytes >= maxMemoryBytes) {
        return 0L;
      }

      final var freeMem = maxMemoryBytes - currentMemoryBytes;
      // Never allocate more than free memory size.
      final var toAllocateBytes = Math.min(freeMem, BLOCK_SIZE_BYTES);
      currentMemoryBytes += toAllocateBytes;

      return toAllocateBytes;
    }

    public void free(long bytes) {

    }

    public void monitorMemory() {
      while (true) {
        //loop over all queues and free what is not used
      }
    }

  }

}
