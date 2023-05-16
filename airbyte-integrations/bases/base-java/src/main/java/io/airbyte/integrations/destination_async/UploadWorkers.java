/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

/**
 * In charge of looking for records in queues and efficiently getting those records uploaded.
 */
@Slf4j
public class UploadWorkers implements AutoCloseable {

  private static final double TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES = Runtime.getRuntime().maxMemory() * 0.8;
  private static final double MAX_CONCURRENT_QUEUES = 10.0;
  private static final double MAX_QUEUE_SIZE_BYTES = TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES / MAX_CONCURRENT_QUEUES;
  private static final long MAX_TIME_BETWEEN_REC_MINS = 15L;

  private static final long SUPERVISOR_INITIAL_DELAY_SECS = 0L;
  private static final long SUPERVISOR_PERIOD_SECS = 1L;
  private final ScheduledExecutorService supervisorThread = Executors.newScheduledThreadPool(1);
  // note: this queue size is unbounded.
  private final ExecutorService workerPool = Executors.newFixedThreadPool(5);
  private final AsyncStreamConsumer.BufferManagerDequeue bufferManagerDequeue;
  private final StreamDestinationFlusher flusher;

  public UploadWorkers(final AsyncStreamConsumer.BufferManagerDequeue bufferManagerDequeue, final StreamDestinationFlusher flusher1) {
    this.bufferManagerDequeue = bufferManagerDequeue;
    this.flusher = flusher1;
  }

  public void start() {
    supervisorThread.scheduleAtFixedRate(this::retrieveWork, SUPERVISOR_INITIAL_DELAY_SECS, SUPERVISOR_PERIOD_SECS,
        TimeUnit.SECONDS);
  }

  private void retrieveWork() {
    // if the total size is > n, flush all buffers
    if (bufferManagerDequeue.getTotalGlobalQueueSizeInMb() > TOTAL_QUEUES_MAX_SIZE_LIMIT_BYTES) {
      flushAll();
    }

    // otherwise, if each individual stream has crossed a specific threshold, flush
    for (Map.Entry<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> entry : bufferManagerDequeue.getBuffers().entrySet()) {
      final var stream = entry.getKey();
      final var exceedSize = bufferManagerDequeue.getQueueSizeInMb(stream) >= MAX_QUEUE_SIZE_BYTES;
      final var tooLongSinceLastRecord = bufferManagerDequeue.getTimeOfLastRecord(stream)
          .map(time -> time.isBefore(Instant.now().minus(MAX_TIME_BETWEEN_REC_MINS, ChronoUnit.MINUTES)))
          .orElse(false);
      if (exceedSize || tooLongSinceLastRecord) {
        flush(stream);
      }
    }
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
      final var queue = bufferManagerDequeue.getBuffer(desc);
      // todo(charles): should not need to know about memory blocking nonsense.
      try {
        log.info("Attempting to read from queue {}..", desc);
        log.info("before size: {}", queue.size());
        var s = Stream.generate(() -> {
          try {
            return queue.take();
          } catch (InterruptedException e) {
            throw new RuntimeException(e);
          }
        }).map(MemoryBoundedLinkedBlockingQueue.MemoryItem::item);
        flusher.flush(desc, s);
        log.info("after size: {}", queue.size());
        log.info("Worker finished flushing..");
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public void close() throws Exception {
    flushAll();

    supervisorThread.shutdown();
    var supervisorShut = supervisorThread.awaitTermination(5L, TimeUnit.MINUTES);
    log.info("Supervisor shut status: {}", supervisorShut);

    log.info("Starting worker pool shutdown..");
    workerPool.shutdown();
    var workersShut = workerPool.awaitTermination(5L, TimeUnit.MINUTES);
    log.info("Workers shut status: {}", workersShut);
  }

}
