/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.FlushWorkers;
import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.state.GlobalAsyncStateManager;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
public class BufferManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferManager.class);

  public static final long TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES = (long) (Runtime.getRuntime().maxMemory() * 0.50);
  private final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers;
  private final BufferEnqueue bufferEnqueue;
  private final BufferDequeue bufferDequeue;
  private final GlobalMemoryManager memoryManager;
  private final ScheduledExecutorService debugLoop = Executors.newSingleThreadScheduledExecutor();

  public BufferManager() {
    LOGGER.info("Memory available to the JVM {}", FileUtils.byteCountToDisplaySize(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES));
    memoryManager = new GlobalMemoryManager(TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES);
    buffers = new ConcurrentHashMap<>();
    final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager();
    bufferEnqueue = new BufferEnqueue(memoryManager, buffers, stateManager);
    bufferDequeue = new BufferDequeue(memoryManager, buffers, stateManager);
    debugLoop.scheduleAtFixedRate(this::printQueueInfo, 0, 10, TimeUnit.SECONDS);
  }

  public BufferEnqueue getBufferEnqueue() {
    return bufferEnqueue;
  }

  public BufferDequeue getBufferDequeue() {
    return bufferDequeue;
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
        .append(String.format("  Global Mem Manager -- max: %s, allocated: %s (%s MB)",
            FileUtils.byteCountToDisplaySize(memoryManager.getMaxMemoryBytes()),
            FileUtils.byteCountToDisplaySize(memoryManager.getCurrentMemoryBytes()),
            (double) memoryManager.getCurrentMemoryBytes() / 1024 / 1024))
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

}
