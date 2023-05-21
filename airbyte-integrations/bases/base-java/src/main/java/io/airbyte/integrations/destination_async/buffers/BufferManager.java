/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination_async.FlushWorkers;
import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.integrations.destination_async.buffers.MemoryBoundedLinkedBlockingQueue;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
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
  private final BufferDequeue bufferManagerDequeue;
  private final GlobalMemoryManager memoryManager;
  private final ScheduledExecutorService debugLoop = Executors.newSingleThreadScheduledExecutor();

  public BufferManager() {
    memoryManager = new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES);
    buffers = new ConcurrentHashMap<>();
    bufferManagerEnqueue = new BufferManagerEnqueue(memoryManager, buffers);
    bufferManagerDequeue = new BufferDequeue(memoryManager, buffers);
    debugLoop.scheduleAtFixedRate(this::printQueueInfo, 0, 10, TimeUnit.SECONDS);
  }

  public BufferManagerEnqueue getBufferManagerEnqueue() {
    return bufferManagerEnqueue;
  }

  public BufferDequeue getBufferManagerDequeue() {
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

      // todo (cgardens) - what if the record being added is bigger than the block size?
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

}
