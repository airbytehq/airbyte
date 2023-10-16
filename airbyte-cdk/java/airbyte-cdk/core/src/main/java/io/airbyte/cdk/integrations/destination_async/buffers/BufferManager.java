/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async.buffers;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.cdk.integrations.destination_async.AirbyteFileUtils;
import io.airbyte.cdk.integrations.destination_async.FlushWorkers;
import io.airbyte.cdk.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.cdk.integrations.destination_async.state.GlobalAsyncStateManager;
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

  public final long maxMemory;
  private final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers;
  private final BufferEnqueue bufferEnqueue;
  private final BufferDequeue bufferDequeue;
  private final GlobalMemoryManager memoryManager;

  private final GlobalAsyncStateManager stateManager;
  private final ScheduledExecutorService debugLoop;

  public static final double MEMORY_LIMIT_RATIO = 0.7;

  public BufferManager() {
    this((long) (Runtime.getRuntime().maxMemory() * MEMORY_LIMIT_RATIO));
  }

  /**
   * @param memoryLimit the amount of estimated memory we allow for all buffers. The
   *        GlobalMemoryManager will apply back pressure once this quota is filled. "Memory" can be
   *        released back once flushing finishes. This number should be large enough we don't block
   *        reading unnecessarily, but small enough we apply back pressure before OOMing.
   */
  public BufferManager(final long memoryLimit) {
    maxMemory = memoryLimit;
    LOGGER.info("Max 'memory' available for buffer allocation {}", FileUtils.byteCountToDisplaySize(maxMemory));
    memoryManager = new GlobalMemoryManager(maxMemory);
    this.stateManager = new GlobalAsyncStateManager(memoryManager);
    buffers = new ConcurrentHashMap<>();
    bufferEnqueue = new BufferEnqueue(memoryManager, buffers, stateManager);
    bufferDequeue = new BufferDequeue(memoryManager, buffers, stateManager);
    debugLoop = Executors.newSingleThreadScheduledExecutor();
    debugLoop.scheduleAtFixedRate(this::printQueueInfo, 0, 10, TimeUnit.SECONDS);
  }

  public GlobalAsyncStateManager getStateManager() {
    return stateManager;
  }

  @VisibleForTesting
  protected GlobalMemoryManager getMemoryManager() {
    return memoryManager;
  }

  @VisibleForTesting
  protected ConcurrentMap<StreamDescriptor, StreamAwareQueue> getBuffers() {
    return buffers;
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
    final var queueInfo = new StringBuilder().append("START OF QUEUE INFO").append(System.lineSeparator())
        .append("This represents an estimation of the size of the elements contain in the in memory buffer.")
        .append(System.lineSeparator());

    queueInfo
        .append(String.format("  Global Mem Manager -- max: %s, allocated: %s (%s MB), %% used: %s",
            AirbyteFileUtils.byteCountToDisplaySize(memoryManager.getMaxMemoryBytes()),
            AirbyteFileUtils.byteCountToDisplaySize(memoryManager.getCurrentMemoryBytes()),
            (double) memoryManager.getCurrentMemoryBytes() / 1024 / 1024,
            (double) memoryManager.getCurrentMemoryBytes() / memoryManager.getMaxMemoryBytes()))
        .append(System.lineSeparator());

    for (final var entry : buffers.entrySet()) {
      final var queue = entry.getValue();
      queueInfo.append(
          String.format("  Queue name: %s, num records: %d, num bytes: %s, allocated bytes: %s",
              entry.getKey().getName(), queue.size(), AirbyteFileUtils.byteCountToDisplaySize(queue.getCurrentMemoryUsage()),
              AirbyteFileUtils.byteCountToDisplaySize(queue.getMaxMemoryUsage())))
          .append(System.lineSeparator());
    }

    queueInfo.append(stateManager.getMemoryUsageMessage())
        .append(System.lineSeparator());

    queueInfo.append("END OF QUEUE INFO");

    log.info(queueInfo.toString());
  }

}
