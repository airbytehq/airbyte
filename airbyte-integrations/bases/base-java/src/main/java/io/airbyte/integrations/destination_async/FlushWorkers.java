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
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

/**
 * Parallel flushing of Destination data.
 * <p>
 * In combination with a {@link DestinationFlushFunction} and the {@link #workerPool}, this class
 * allows for parallel data flushing.
 * <p>
 * Parallelising is important as it 1) minimises Destination backpressure 2) minimises the effect of
 * IO pauses on Destination performance. The second point is particularly important since majority
 * of Destination work is IO bound.
 * <p>
 * The {@link #supervisorThread} assigns work to worker threads by looping over
 * {@link #bufferManagerDequeue} - a dequeue interface over in-memory queues of
 * {@link AirbyteMessage}. See {@link #retrieveWork()} for assignment logic.
 * <p>
 * Within a worker thread, a worker best-effort reads a
 * {@link DestinationFlushFunction#getOptimalBatchSizeBytes()} batch from the in-memory stream and
 * calls {@link DestinationFlushFunction#flush(StreamDescriptor, Stream)} on the returned data.
 */
@Slf4j
public class FlushWorkers implements AutoCloseable {

  private static final long MAX_TIME_BETWEEN_REC_MINS = 5L;
  private static final long SUPERVISOR_INITIAL_DELAY_SECS = 0L;
  private static final long SUPERVISOR_PERIOD_SECS = 1L;
  private static final long DEBUG_INITIAL_DELAY_SECS = 0L;
  private static final long DEBUG_PERIOD_SECS = 10L;
  private final ScheduledExecutorService supervisorThread = Executors.newScheduledThreadPool(1);
  private final ExecutorService workerPool = Executors.newFixedThreadPool(5);
  private final BufferManager.BufferManagerDequeue bufferManagerDequeue;
  private final DestinationFlushFunction flusher;
  private final ScheduledExecutorService debugLoop = Executors.newSingleThreadScheduledExecutor();

  public FlushWorkers(final BufferManager.BufferManagerDequeue bufferManagerDequeue, final DestinationFlushFunction flushFunction) {
    this.bufferManagerDequeue = bufferManagerDequeue;
    flusher = flushFunction;
  }

  public void start() {
    supervisorThread.scheduleAtFixedRate(this::retrieveWork, SUPERVISOR_INITIAL_DELAY_SECS, SUPERVISOR_PERIOD_SECS,
        TimeUnit.SECONDS);
    debugLoop.scheduleAtFixedRate(this::printWorkerInfo, DEBUG_INITIAL_DELAY_SECS, DEBUG_PERIOD_SECS, TimeUnit.SECONDS);
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

}
