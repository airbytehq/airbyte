/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

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
 * {@link #bufferDequeue} - a dequeue interface over in-memory queues of {@link AirbyteMessage}. See
 * {@link #retrieveWork()} for assignment logic.
 * <p>
 * Within a worker thread, a worker best-effort reads a
 * {@link DestinationFlushFunction#getOptimalBatchSizeBytes()} batch from the in-memory stream and
 * calls {@link DestinationFlushFunction#flush(StreamDescriptor, Stream)} on the returned data.
 */
@Slf4j
public class FlushWorkers implements AutoCloseable {

  public static final long TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES = (long) (Runtime.getRuntime().maxMemory() * 0.8);
  private static final long QUEUE_FLUSH_THRESHOLD_BYTES = 10 * 1024 * 1024; // 10MB
  private static final long MAX_TIME_BETWEEN_REC_MINS = 5L;
  private static final long SUPERVISOR_INITIAL_DELAY_SECS = 0L;
  private static final long SUPERVISOR_PERIOD_SECS = 1L;
  private static final long DEBUG_INITIAL_DELAY_SECS = 0L;
  private static final long DEBUG_PERIOD_SECS = 10L;
  private final ScheduledExecutorService supervisorThread = Executors.newScheduledThreadPool(1);
  private final ExecutorService workerPool = Executors.newFixedThreadPool(5);
  private final BufferDequeue bufferDequeue;
  private final DestinationFlushFunction flusher;
  private final ScheduledExecutorService debugLoop = Executors.newSingleThreadScheduledExecutor();
  private final ConcurrentHashMap<StreamDescriptor, AtomicInteger> streamToInProgressWorkers = new ConcurrentHashMap<>();

  public FlushWorkers(final BufferDequeue bufferDequeue, final DestinationFlushFunction flushFunction) {
    this.bufferDequeue = bufferDequeue;
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

    debugLoop.shutdownNow();
  }

  private void retrieveWork() {
    // todo (cgardens) - i'm not convinced this makes sense. as we get close to the limit, we should
    // flush more eagerly, but "flush all" is never a particularly useful thing in this world.
    // if the total size is > n, flush all buffers
    if (bufferDequeue.getTotalGlobalQueueSizeBytes() > TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES) {
      flushAll();
      return;
    }

    final ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) workerPool;
    var allocatableThreads = threadPoolExecutor.getMaximumPoolSize() - threadPoolExecutor.getActiveCount();

    // todo (cgardens) - build a score to prioritize which queue to flush next. e.g. if a queue is very
    // large, flush it first. if a queue has not been flushed in a while, flush it next.
    // otherwise, if each individual stream has crossed a specific threshold, flush
    for (final StreamDescriptor stream : bufferDequeue.getBufferedStreams()) {
      if (allocatableThreads == 0) {
        break;
      }

      // while we allow out-of-order processing for speed improvements via multiple workers reading from
      // the same queue, also avoid scheduling more workers than what is already in progress.
      final var inProgressSizeByte = (bufferDequeue.getQueueSizeBytes(stream).get() -
          streamToInProgressWorkers.getOrDefault(stream, new AtomicInteger(0)).get() * QUEUE_FLUSH_THRESHOLD_BYTES);
      final var exceedSize = inProgressSizeByte >= QUEUE_FLUSH_THRESHOLD_BYTES;
      final var tooLongSinceLastRecord = bufferDequeue.getTimeOfLastRecord(stream)
          .map(time -> time.isBefore(Instant.now().minus(MAX_TIME_BETWEEN_REC_MINS, ChronoUnit.MINUTES)))
          .orElse(false);

      if (exceedSize || tooLongSinceLastRecord) {
        log.info(
            "Allocated stream {}, exceedSize:{}, tooLongSinceLastRecord: {}, bytes in queue: {} computed in-progress bytes: {} , threshold bytes: {}",
            stream.getName(), exceedSize, tooLongSinceLastRecord,
            FileUtils.byteCountToDisplaySize(bufferDequeue.getQueueSizeBytes(stream).get()),
            FileUtils.byteCountToDisplaySize(inProgressSizeByte),
            FileUtils.byteCountToDisplaySize(QUEUE_FLUSH_THRESHOLD_BYTES));
        allocatableThreads--;
        if (streamToInProgressWorkers.containsKey(stream)) {
          streamToInProgressWorkers.get(stream).getAndAdd(1);
        } else {
          streamToInProgressWorkers.put(stream, new AtomicInteger(1));
        }
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
    for (final StreamDescriptor desc : bufferDequeue.getBufferedStreams()) {
      flush(desc);
    }
  }

  private void flush(final StreamDescriptor desc) {
    workerPool.submit(() -> {
      log.info("Worker picked up work..");
      try {
        log.info("Attempting to read from queue {}. Current queue size: {}", desc, bufferDequeue.getQueueSizeInRecords(desc).get());

        try (final var batch = bufferDequeue.take(desc, flusher.getOptimalBatchSizeBytes())) {
          flusher.flush(desc, batch.getData());
        }

        log.info("Worker finished flushing. Current queue size: {}", bufferDequeue.getQueueSizeInRecords(desc));
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

}
