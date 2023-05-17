/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static io.airbyte.integrations.destination_async.BufferManager.QUEUE_FLUSH_THRESHOLD;
import static io.airbyte.integrations.destination_async.BufferManager.TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import lombok.extern.slf4j.Slf4j;

/**
 * In charge of looking for records in queues and efficiently getting those records uploaded.
 */
@Slf4j
public class UploadWorkers implements AutoCloseable {

  private static final long MAX_TIME_BETWEEN_REC_MINS = 5L;

  private static final long SUPERVISOR_INITIAL_DELAY_SECS = 0L;
  private static final long SUPERVISOR_PERIOD_SECS = 1L;
  private final ScheduledExecutorService supervisorThread = Executors.newScheduledThreadPool(1);
  // note: this queue size is unbounded.
  private final ExecutorService workerPool = Executors.newFixedThreadPool(5);
  private final BufferManager.BufferManagerDequeue bufferManagerDequeue;
  private final StreamDestinationFlusher flusher;
  private final ScheduledExecutorService debugLoop = Executors.newSingleThreadScheduledExecutor();

  public UploadWorkers(final BufferManager.BufferManagerDequeue bufferManagerDequeue, final StreamDestinationFlusher flusher1) {
    this.bufferManagerDequeue = bufferManagerDequeue;
    flusher = flusher1;
  }

  public void start() {
    supervisorThread.scheduleAtFixedRate(this::retrieveWork, SUPERVISOR_INITIAL_DELAY_SECS, SUPERVISOR_PERIOD_SECS,
        TimeUnit.SECONDS);
  }

  private void retrieveWork() {
    // todo (cgardens) - i'm not convinced this makes sense. as we get close to the limit, we should
    // flush more eagerly, but "flush all" is never a particularly useful thing in this world.
    // if the total size is > n, flush all buffers
    if (bufferManagerDequeue.getTotalGlobalQueueSizeBytes() > TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES) {
      flushAll();
    }

    // todo (cgardens) - build a score to prioritize which queue to flush next. e.g. if a queue is very
    // large, flush it first. if a queue has not been flushed in a while, flush it next.
    // otherwise, if each individual stream has crossed a specific threshold, flush
    for (final Map.Entry<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> entry : bufferManagerDequeue.getBuffers().entrySet()) {
      final var stream = entry.getKey();
      final var exceedSize = bufferManagerDequeue.getQueueSizeBytes(stream) >= QUEUE_FLUSH_THRESHOLD;
      final var tooLongSinceLastRecord = bufferManagerDequeue.getTimeOfLastRecord(stream)
          .map(time -> time.isBefore(Instant.now().minus(MAX_TIME_BETWEEN_REC_MINS, ChronoUnit.MINUTES)))
          .orElse(false);
      if (exceedSize || tooLongSinceLastRecord) {
        flush(stream);
      }
    }
  }

  private void printWorkerInfo() {
    final var workerInfo = new StringBuilder().append("WORKER INFO").append(System.lineSeparator());

    final ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) workerPool;

    final int queueSize = threadPoolExecutor.getQueue().size();
    final int activeCount = threadPoolExecutor.getActiveCount();

    workerInfo.append(String.format("  Pool queue size: %d, Active threads: %d", queueSize, activeCount));
    log.info(workerInfo.toString());

  }

  private void flushAll() {
    log.info("Flushing all buffers..");
    for (final StreamDescriptor desc : bufferManagerDequeue.getBuffers().keySet()) {
      flush(desc);
    }
  }

  private void flush(final StreamDescriptor desc) {
    workerPool.submit(() -> {
      log.info("Worker picked up work..");
      try {
        log.info("Attempting to read from queue {}. Current queue size: {}", desc, bufferManagerDequeue.getQueueSizeInRecords(desc));

        try (final var batch = bufferManagerDequeue.take(desc, flusher.getOptimalBatchSizeBytes())) {
          flusher.flush(desc, batch.getData());
        }

        log.info("Worker finished flushing. Current queue size: {}", bufferManagerDequeue.getQueueSizeInRecords(desc));
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public void close() throws Exception {
    flushAll();

    supervisorThread.shutdown();
    final var supervisorShut = supervisorThread.awaitTermination(5L, TimeUnit.MINUTES);
    log.info("Supervisor shut status: {}", supervisorShut);

    log.info("Starting worker pool shutdown..");
    workerPool.shutdown();
    final var workersShut = workerPool.awaitTermination(5L, TimeUnit.MINUTES);
    log.info("Workers shut status: {}", workersShut);
  }

}

// var s = Stream.generate(() -> {
// try {
// return queue.take();
// } catch (InterruptedException e) {
// throw new RuntimeException(e);
// }
// }).map(MemoryBoundedLinkedBlockingQueue.MemoryItem::item);
