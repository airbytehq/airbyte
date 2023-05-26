/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

/**
 * This classes finds the best, next stream to flush.
 */
@Slf4j
public class DetectStreamToFlush {

  private static final double EAGER_FLUSH_THRESHOLD = 0.90;
  private static final long QUEUE_FLUSH_THRESHOLD_BYTES = 10 * 1024 * 1024; // 10MB
  private static final long MAX_TIME_BETWEEN_REC_MINS = 5L;
  private final BufferDequeue bufferDequeue;
  private final RunningFlushWorkers runningFlushWorkers;
  private final AtomicBoolean isClosing;

  public DetectStreamToFlush(final BufferDequeue bufferDequeue, final RunningFlushWorkers runningFlushWorkers, final AtomicBoolean isClosing) {
    this.bufferDequeue = bufferDequeue;
    this.runningFlushWorkers = runningFlushWorkers;
    this.isClosing = isClosing;
  }

  public Optional<StreamDescriptor> getNextStreamToFlush() {
    return getNextStreamToFlush(computeQueueThreshold());
  }

  /**
   * We have a minimum threshold for the size of a queue before we will flush it. The threshold helps
   * us avoid uploading small amounts of data at a time, which is really resource inefficient.
   * Depending on certain conditions, we dynamically adjust this threshold.
   * <p>
   * Rules:
   * <li>default - By default the, the threshold is a set at a constant:
   * QUEUE_FLUSH_THRESHOLD_BYTES.</li>
   * <li>memory pressure - If we are getting close to maxing out available memory, we reduce it to
   * zero. This helps in the case where there are a lot of streams, so total memory usage is high, but
   * each individual queue isn't that large.</li>
   * <li>closing - If the Flush Worker is closing, we reduce it to zero. We close when all records
   * have been added to the queue, at which point, our goal is to flush out any non-empty queues.</li>
   *
   * @return based on the conditions, the threshold in bytes.
   */
  @VisibleForTesting
  long computeQueueThreshold() {
    final boolean isBuffer90Full =
        EAGER_FLUSH_THRESHOLD <= (double) bufferDequeue.getTotalGlobalQueueSizeBytes() / bufferDequeue.getMaxQueueSizeBytes();
    // when we are closing or queues are very fully, flush regardless of how few items are in the queue.
    return isClosing.get() || isBuffer90Full ? 0 : QUEUE_FLUSH_THRESHOLD_BYTES;
  }

  // todo (cgardens) - improve prioritization by getting a better estimate of how much data running
  // workers will process. we have access to their batch sizes after all!
  /**
   * Iterates over streams until it finds one that is ready to flush. Streams are ordered by priority.
   * If no stream is ready, it returns an empty optional.
   * <p>
   * A stream is ready to flush if it either meets a size threshold or a time threshold. For the size
   * threshold, the size of the data in the queue is compared to the threshold that is passed into
   * this method.
   * <p>
   * One caveat, is that if that stream already has a worker running, we "penalize" its size. We do
   * this by computing what the size of the queue would be after the running workers for that queue
   * complete. This is based on a dumb estimate of how much data a worker can process. There is an
   * opportunity for optimization here, by being smarter about predicting how much data a running
   * worker is likely to process.
   * <p>
   * Finally, the time trigger is based on the last time a record was added to the queue. We don't
   * want records to sit forever, even if the queue is not that full (bad for time to value for
   * users). Also, the more time passes since a record was added, the less likely another record is
   * coming (caveat is CDC where it's random).
   *
   * @param queueSizeThresholdBytes - the size threshold to use for determining if a stream is ready
   *        to flush.
   * @return the next stream to flush. if no stream is ready to flush, empty.
   */
  @VisibleForTesting
  Optional<StreamDescriptor> getNextStreamToFlush(final long queueSizeThresholdBytes) {
    for (final StreamDescriptor stream : orderStreamsByPriority(bufferDequeue.getBufferedStreams())) {
      // while we allow out-of-order processing for speed improvements via multiple workers reading from
      // the same queue, also avoid scheduling more workers than what is already in progress.
      final long runningBytesEstimate = runningFlushWorkers.getNumFlushWorkers(stream) * QUEUE_FLUSH_THRESHOLD_BYTES;
      final long inQueueBytes = bufferDequeue.getQueueSizeBytes(stream).orElseThrow() - runningBytesEstimate;
      final var isQueueSizeExceedsThreshold = inQueueBytes > queueSizeThresholdBytes;
      final var isTooLongSinceLastRecord = bufferDequeue.getTimeOfLastRecord(stream)
          .map(time -> time.isBefore(Instant.now().minus(MAX_TIME_BETWEEN_REC_MINS, ChronoUnit.MINUTES)))
          .orElse(false);

      final String streamInfo = String.format(
          "Flushing stream %s - %s, time trigger: %s, size trigger: %s current threshold b: %s, queue size b: %s, in-progress estimate b: %s, in queue b: %s",
          stream.getNamespace(),
          stream.getName(),
          isTooLongSinceLastRecord,
          isQueueSizeExceedsThreshold,
          AirbyteFileUtils.byteCountToDisplaySize(queueSizeThresholdBytes),
          AirbyteFileUtils.byteCountToDisplaySize(bufferDequeue.getQueueSizeBytes(stream).orElseThrow()),
          AirbyteFileUtils.byteCountToDisplaySize(runningBytesEstimate),
          AirbyteFileUtils.byteCountToDisplaySize(inQueueBytes));
      log.debug("computed: {}", streamInfo);

      if (isQueueSizeExceedsThreshold || isTooLongSinceLastRecord) {
        log.info("Flushing: {}", streamInfo);

        return Optional.of(stream);
      }
    }
    return Optional.empty();
  }

  /**
   * Sort stream descriptors in order of priority with which we would want to flush them.
   * <p>
   * Priority is in the following order:
   * <li>1. size in queue (descending)</li>
   * <li>2. time since last record (ascending)</li>
   * <li>3. alphabetical by namespace + stream name.</li>
   * <p>
   * In other words, move the biggest queues first, because they are most likely to use available
   * resources optimally. Then get rid of old stuff (time to value for the user and, generally, as the
   * age of the last record grows, the likelihood of getting any more records from that stream
   * decreases, so by flushing them, we can totally complete that stream. Finally, tertiary sort by
   * name so the order is deterministic.
   *
   * @param streams streams to sort.
   * @return streams sorted by priority.
   */
  @VisibleForTesting
  List<StreamDescriptor> orderStreamsByPriority(final Set<StreamDescriptor> streams) {
    return streams.stream()
        .sorted(Comparator.comparing((StreamDescriptor s) -> bufferDequeue.getQueueSizeBytes(s).orElseThrow(), Comparator.reverseOrder())
            .thenComparing(s -> bufferDequeue.getTimeOfLastRecord(s).orElseThrow())
            .thenComparing(s -> s.getNamespace() + s.getName()))
        .collect(Collectors.toList());
  }

}
