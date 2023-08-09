/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.integrations.destination_async.buffers.StreamAwareQueue.MessageWithMeta;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.state.FlushFailure;
import io.airbyte.integrations.destination_async.state.GlobalAsyncStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
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
  private final RunningFlushWorkers runningFlushWorkers;
  private final DetectStreamToFlush detectStreamToFlush;

  private final FlushFailure flushFailure;

  private final AtomicBoolean isClosing;
  private final GlobalAsyncStateManager stateManager;

  public FlushWorkers(final BufferDequeue bufferDequeue,
                      final DestinationFlushFunction flushFunction,
                      final Consumer<AirbyteMessage> outputRecordCollector,
                      final FlushFailure flushFailure,
                      final GlobalAsyncStateManager stateManager) {
    this.bufferDequeue = bufferDequeue;
    this.outputRecordCollector = outputRecordCollector;
    this.flushFailure = flushFailure;
    this.stateManager = stateManager;
    flusher = flushFunction;
    debugLoop = Executors.newSingleThreadScheduledExecutor();
    supervisorThread = Executors.newScheduledThreadPool(1);
    workerPool = Executors.newFixedThreadPool(5);
    isClosing = new AtomicBoolean(false);
    runningFlushWorkers = new RunningFlushWorkers();
    detectStreamToFlush = new DetectStreamToFlush(bufferDequeue, runningFlushWorkers, isClosing, flusher);
  }

  public void start() {
    log.info("Start async buffer supervisor");
    supervisorThread.scheduleAtFixedRate(this::retrieveWork,
        SUPERVISOR_INITIAL_DELAY_SECS,
        SUPERVISOR_PERIOD_SECS,
        TimeUnit.SECONDS);
    debugLoop.scheduleAtFixedRate(this::printWorkerInfo,
        DEBUG_INITIAL_DELAY_SECS,
        DEBUG_PERIOD_SECS,
        TimeUnit.SECONDS);
  }

  private void retrieveWork() {
    try {
      // This will put a new log line every second which is too much, sampling it doesn't bring much value
      // so it is set to debug
      log.debug("Retrieve Work -- Finding queues to flush");
      final ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) workerPool;
      int allocatableThreads = threadPoolExecutor.getMaximumPoolSize() - threadPoolExecutor.getActiveCount();

      while (allocatableThreads > 0) {
        final Optional<StreamDescriptor> next = detectStreamToFlush.getNextStreamToFlush();

        if (next.isPresent()) {
          final StreamDescriptor desc = next.get();
          final UUID flushWorkerId = UUID.randomUUID();
          runningFlushWorkers.trackFlushWorker(desc, flushWorkerId);
          allocatableThreads--;
          flush(desc, flushWorkerId);
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

  private void printWorkerInfo() {
    final var workerInfo = new StringBuilder().append("WORKER INFO").append(System.lineSeparator());

    final ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) workerPool;

    final int queueSize = threadPoolExecutor.getQueue().size();
    final int activeCount = threadPoolExecutor.getActiveCount();

    workerInfo.append(String.format("  Pool queue size: %d, Active threads: %d", queueSize, activeCount));
    log.info(workerInfo.toString());

  }

  private void flush(final StreamDescriptor desc, final UUID flushWorkerId) {
    workerPool.submit(() -> {
      log.info("Flush Worker ({}) -- Worker picked up work.", humanReadableFlushWorkerId(flushWorkerId));
      try {
        log.info("Flush Worker ({}) -- Attempting to read from queue namespace: {}, stream: {}.",
            humanReadableFlushWorkerId(flushWorkerId),
            desc.getNamespace(),
            desc.getName());

        try (final var batch = bufferDequeue.take(desc, flusher.getOptimalBatchSizeBytes())) {
          runningFlushWorkers.registerBatchSize(desc, flushWorkerId, batch.getSizeInBytes());
          final Map<Long, Long> stateIdToCount = batch.getData()
              .stream()
              .map(MessageWithMeta::stateId)
              .collect(Collectors.groupingBy(
                  stateId -> stateId,
                  Collectors.counting()));
          log.info("Flush Worker ({}) -- Batch contains: {} records, {} bytes.",
              humanReadableFlushWorkerId(flushWorkerId),
              batch.getData().size(),
              AirbyteFileUtils.byteCountToDisplaySize(batch.getSizeInBytes()));

          flusher.flush(desc, batch.getData().stream().map(MessageWithMeta::message));
          emitStateMessages(batch.flushStates(stateIdToCount));
        }

        log.info("Flush Worker ({}) -- Worker finished flushing. Current queue size: {}",
            humanReadableFlushWorkerId(flushWorkerId),
            bufferDequeue.getQueueSizeInRecords(desc).orElseThrow());
      } catch (final Exception e) {
        log.error(String.format("Flush Worker (%s) -- flush worker error: ", humanReadableFlushWorkerId(flushWorkerId)), e);
        flushFailure.propagateException(e);
        throw new RuntimeException(e);
      } finally {
        runningFlushWorkers.completeFlushWorker(desc, flushWorkerId);
      }
    });
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

    // before shutting down the supervisor, flush all state.
    emitStateMessages(stateManager.flushStates());
    supervisorThread.shutdown();
    final var supervisorShut = supervisorThread.awaitTermination(5L, TimeUnit.MINUTES);
    log.info("Closing flush workers -- Supervisor shutdown status: {}", supervisorShut);

    log.info("Closing flush workers -- Starting worker pool shutdown..");
    workerPool.shutdown();
    final var workersShut = workerPool.awaitTermination(5L, TimeUnit.MINUTES);
    log.info("Closing flush workers -- Workers shutdown status: {}", workersShut);

    debugLoop.shutdownNow();
  }

  private void emitStateMessages(final List<PartialAirbyteMessage> partials) {
    partials
        .stream()
        .map(partial -> Jsons.deserialize(partial.getSerialized(), AirbyteMessage.class))
        .forEach(outputRecordCollector);
  }

  private static String humanReadableFlushWorkerId(final UUID flushWorkerId) {
    return flushWorkerId.toString().substring(0, 5);
  }

}
