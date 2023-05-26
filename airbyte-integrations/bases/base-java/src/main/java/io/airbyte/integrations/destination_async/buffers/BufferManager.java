/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination_async.AirbyteFileUtils;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
public class BufferManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferManager.class);

  public final long maxMemory;
  private final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers;
  private final BufferEnqueue bufferEnqueue;
  private final BufferDequeue bufferDequeue;
  private final GlobalMemoryManager memoryManager;
  private final ScheduledExecutorService debugLoop;

  public BufferManager() {
    this((long) (Runtime.getRuntime().maxMemory() * 0.8));
  }

  @VisibleForTesting
  public BufferManager(final long memoryLimit) {
    maxMemory = memoryLimit;
    LOGGER.info("Memory available from totalMemory: {}", AirbyteFileUtils.byteCountToDisplaySize(Runtime.getRuntime().totalMemory()));
    LOGGER.info("Memory available from maxMemory: {}", AirbyteFileUtils.byteCountToDisplaySize(Runtime.getRuntime().maxMemory()));
    LOGGER.info("Memory available from freeMemory: {}", AirbyteFileUtils.byteCountToDisplaySize(Runtime.getRuntime().freeMemory()));
    memoryManager = new GlobalMemoryManager(maxMemory);
    buffers = new ConcurrentHashMap<>();
    final GlobalAsyncStateManager stateManager = new GlobalAsyncStateManager(memoryManager);
    bufferEnqueue = new BufferEnqueue(memoryManager, buffers, stateManager);
    bufferDequeue = new BufferDequeue(memoryManager, buffers, stateManager);
    debugLoop = Executors.newSingleThreadScheduledExecutor();
    debugLoop.scheduleAtFixedRate(this::printQueueInfo, 0, 2, TimeUnit.SECONDS);
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
        .append(String.format("  Global Mem Manager -- max: %s in megabytes, allocated: %s MB",
            (double) memoryManager.getMaxMemoryBytes() / 1024 / 1024,
            (double) memoryManager.getCurrentMemoryBytes() / 1024 / 1024,
            (double) memoryManager.getCurrentMemoryBytes() / 1024 / 1024))
        .append(System.lineSeparator());

    queueInfo
        .append(String.format("  Runtime.freeMemory(): %s MB",
            Runtime.getRuntime().freeMemory() / 1024 / 1024))
        .append(System.lineSeparator());

    for (final var entry : buffers.entrySet()) {
      final var queue = entry.getValue();
      queueInfo.append(
          String.format("  Queue name: %s, num records: %d, num mb: %s",
              entry.getKey().getName(), queue.size(), queue.getCurrentMemoryUsage() / 1024 / 1024))
          .append(System.lineSeparator());
    }
    log.info(queueInfo.toString());
  }

}
