/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.integrations.destination_async.buffers.StreamAwareQueue.MessageWithMeta;
import io.airbyte.integrations.destination_async.state.FlushFailure;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

/**
 * Parallel flushing of Destination data.
 * <p>
 * In combination with a {@link DestinationFlushFunction} and the {@link #workerPool}, this class
 * allows for parallel data flushing.
 * <p>
 * Parallelising is important as it 1) minimises Destination backpressure 2) minimises the effect of
 * IO pauses on Destination performance. The second point is particularly important since a majority
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

  private static final long QUEUE_FLUSH_THRESHOLD_BYTES = 10 * 1024 * 1024; // 10MB
  private static final long MAX_TIME_BETWEEN_REC_MINS = 5L;
  private static final long SUPERVISOR_INITIAL_DELAY_SECS = 0L;
  private static final long SUPERVISOR_PERIOD_SECS = 1L;
  private static final long DEBUG_INITIAL_DELAY_SECS = 0L;
  private static final long DEBUG_PERIOD_SECS = 10L;
  private final ScheduledExecutorService supervisorThread;
  private final ExecutorService workerPool;
  private final BufferDequeue bufferDequeue;
  private final DestinationFlushFunction flusher;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final ScheduledExecutorService debugLoop;
  private final ConcurrentHashMap<StreamDescriptor, AtomicInteger> streamToInProgressWorkers;

  private final FlushFailure flushFailure;

  private final AtomicBoolean isClosing;

  public FlushWorkers(final BufferDequeue bufferDequeue,
                      final DestinationFlushFunction flushFunction,
                      final Consumer<AirbyteMessage> outputRecordCollector,
                      final FlushFailure flushFailure) {
    this.bufferDequeue = bufferDequeue;
    flusher = flushFunction;
    this.outputRecordCollector = outputRecordCollector;
    this.flushFailure = flushFailure;
    streamToInProgressWorkers = new ConcurrentHashMap<>();
    debugLoop = Executors.newSingleThreadScheduledExecutor();
    supervisorThread = Executors.newScheduledThreadPool(1);
    workerPool = Executors.newFixedThreadPool(5);
    isClosing = new AtomicBoolean(false);
  }

  public void start() {
    supervisorThread.scheduleAtFixedRate(this::retrieveWork,
        SUPERVISOR_INITIAL_DELAY_SECS,
        SUPERVISOR_PERIOD_SECS,
        TimeUnit.SECONDS);
    debugLoop.scheduleAtFixedRate(this::printWorkerInfo,
        DEBUG_INITIAL_DELAY_SECS,
        DEBUG_PERIOD_SECS,
        TimeUnit.SECONDS);
  }

  @Override
  public void close() throws Exception {
    log.info("Closing flush workers -- waiting for all buffers to flush");
    isClosing.set(true);
    // wait for all buffers to be flushed.
    while (true) {
      final Map<StreamDescriptor, Long> streamDescriptorToRemainingRecords = bufferDequeue.getBufferedStreams()
          .stream()
          .collect(Collectors.toMap(desc -> desc, desc -> bufferDequeue.getQueueSizeInRecords(desc).orElseThrow()));

      final boolean anyRecordsLeft = streamDescriptorToRemainingRecords
          .values()
          .stream()
          .anyMatch(size -> size > 0);

      if (!anyRecordsLeft) {
        break;
      }

      final var workerInfo = new StringBuilder().append("REMAINING_BUFFERS_INFO").append(System.lineSeparator());
      streamDescriptorToRemainingRecords.entrySet()
          .stream()
          .filter(entry -> entry.getValue() > 0)
          .forEach(entry -> workerInfo.append(String.format("  Namespace: %s Stream: %s -- remaining records: %d",
              entry.getKey().getNamespace(),
              entry.getKey().getName(),
              entry.getValue())));
      log.info(workerInfo.toString());
      log.info("Waiting for all streams to flush.");
      Thread.sleep(1000);
    }
    log.info("Closing flush workers -- all buffers flushed");

    supervisorThread.shutdown();
    final var supervisorShut = supervisorThread.awaitTermination(5L, TimeUnit.MINUTES);
    log.info("Closing flush workers -- Supervisor shutdown status: {}", supervisorShut);

    log.info("Closing flush workers -- Starting worker pool shutdown..");
    workerPool.shutdown();
    final var workersShut = workerPool.awaitTermination(5L, TimeUnit.MINUTES);
    log.info("Closing flush workers -- Workers shutdown status: {}", workersShut);

    debugLoop.shutdownNow();
  }

  private void retrieveWork() {
    try {
      log.info("Retrieve Work -- Finding queues to flush");
      final ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) workerPool;
      int allocatableThreads = threadPoolExecutor.getMaximumPoolSize() - threadPoolExecutor.getActiveCount();

      while (allocatableThreads > 0) {
        // when we are closing, flush regardless of how few items are in the queue.
        final long computedQueueThreshold = isClosing.get() ? 0 : QUEUE_FLUSH_THRESHOLD_BYTES;

        final Optional<StreamDescriptor> next = getNextStreamToFlush(computedQueueThreshold);

        if (next.isPresent()) {
          final StreamDescriptor desc = next.get();
          if (streamToInProgressWorkers.containsKey(desc)) {
            streamToInProgressWorkers.get(desc).getAndAdd(1);
          } else {
            streamToInProgressWorkers.put(desc, new AtomicInteger(1));
          }
          allocatableThreads--;
          flush(desc);
        } else {
          break;
        }
      }
    } catch (final Exception e) {
      log.error("Flush worker error: ", e);
      flushFailure.propagateException(e);
      throw new RuntimeException(e);
    }
  }

  private Optional<StreamDescriptor> getNextStreamToFlush(final long queueSizeThresholdBytes) {
    // todo (cgardens) - prefer finding a new stream over flushing more records from a stream that's
    // already flushing. this random is a lazy verison of this.
    final ArrayList<StreamDescriptor> shuffled = new ArrayList<>(bufferDequeue.getBufferedStreams());
    Collections.shuffle(shuffled);
    for (final StreamDescriptor stream : shuffled) {
      // while we allow out-of-order processing for speed improvements via multiple workers reading from
      // the same queue, also avoid scheduling more workers than what is already in progress.
      final long runningBytesEstimate = streamToInProgressWorkers.getOrDefault(stream, new AtomicInteger(0)).get() * QUEUE_FLUSH_THRESHOLD_BYTES;
      final long queueSizeAfterInProgress = bufferDequeue.getQueueSizeBytes(stream).orElseThrow() - runningBytesEstimate;
      final var isQueueSizeExceedsThreshold = queueSizeAfterInProgress >= queueSizeThresholdBytes;
      final var isTooLongSinceLastRecord = bufferDequeue.getTimeOfLastRecord(stream)
          .map(time -> time.isBefore(Instant.now().minus(MAX_TIME_BETWEEN_REC_MINS, ChronoUnit.MINUTES)))
          .orElse(false);

      final String streamInfo = String.format(
          "Flushing stream %s - %s, time trigger: %s, size trigger: %s current threshold: %s, queue size: %s, in-progress estimate: %s, adjusted queue size: %s",
          stream.getNamespace(),
          stream.getName(),
          isTooLongSinceLastRecord,
          isQueueSizeExceedsThreshold,
          queueSizeThresholdBytes,
          bufferDequeue.getQueueSizeBytes(stream).orElseThrow(),
          runningBytesEstimate,
          queueSizeAfterInProgress);
      // todo make this debug
      log.info("computed: {}", streamInfo);

      if (isQueueSizeExceedsThreshold || isTooLongSinceLastRecord) {
        log.info("Flushing: {}", streamInfo);

        return Optional.of(stream);
      }
    }
    return Optional.empty();
  }

  private void printWorkerInfo() {
    final var workerInfo = new StringBuilder().append("WORKER INFO").append(System.lineSeparator());

    final ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) workerPool;

    final int queueSize = threadPoolExecutor.getQueue().size();
    final int activeCount = threadPoolExecutor.getActiveCount();

    workerInfo.append(String.format("  Pool queue size: %d, Active threads: %d", queueSize, activeCount));
    log.info(workerInfo.toString());

  }

  private void flush(final StreamDescriptor desc) {
    workerPool.submit(() -> {
      final String flushWorkerId = UUID.randomUUID().toString().substring(0, 5);
      log.info("Flush Worker ({}) -- Worker picked up work.", flushWorkerId);
      try {
        log.info("Flush Worker ({}) -- Attempting to read from queue namespace: {}, stream: {}.",
            flushWorkerId,
            desc.getNamespace(),
            desc.getName());

        try (final var batch = bufferDequeue.take(desc, flusher.getOptimalBatchSizeBytes())) {
          final Map<Long, Long> stateIdToCount = batch.getData()
              .stream()
              .map(MessageWithMeta::stateId)
              .collect(Collectors.groupingBy(
                  stateId -> stateId,
                  Collectors.counting()));
          final long totalSize = stateIdToCount.values().stream().mapToLong(v -> v).sum();
          log.info("Flush Worker ({}) -- Batch contains: {} records.",
              flushWorkerId,
              batch.getData().size());

          flusher.flush(desc, batch.getData().stream().map(MessageWithMeta::message));
          batch.flushStates(stateIdToCount).forEach(outputRecordCollector);
        }

        log.info("Flush Worker ({}) -- Worker finished flushing. Current queue size: {}",
            flushWorkerId,
            bufferDequeue.getQueueSizeInRecords(desc).orElseThrow());
      } catch (final Exception e) {
        log.error(String.format("Flush Worker (%s) -- flush worker error: ", flushWorkerId), e);
        flushFailure.propagateException(e);
        throw new RuntimeException(e);
      } finally {
        streamToInProgressWorkers.get(desc).getAndDecrement();
      }
    });
  }

}
