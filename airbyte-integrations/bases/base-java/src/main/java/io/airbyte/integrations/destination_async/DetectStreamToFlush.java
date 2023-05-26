/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import lombok.extern.slf4j.Slf4j;

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

  @VisibleForTesting
  long computeQueueThreshold() {
    final boolean isBuffer90Full =
        EAGER_FLUSH_THRESHOLD <= (double) bufferDequeue.getTotalGlobalQueueSizeBytes() / bufferDequeue.getTotalGlobalQueueSizeBytes();
    // when we are closing or queues are very fully, flush regardless of how few items are in the queue.
    return isClosing.get() || isBuffer90Full ? 0 : QUEUE_FLUSH_THRESHOLD_BYTES;
  }

  @VisibleForTesting
  Optional<StreamDescriptor> getNextStreamToFlush(final long queueSizeThresholdBytes) {
    // todo (cgardens) - prefer finding a new stream over flushing more records from a stream that's
    // already flushing. this random is a lazy verison of this.
    final ArrayList<StreamDescriptor> shuffled = new ArrayList<>(bufferDequeue.getBufferedStreams());
    Collections.shuffle(shuffled);
    for (final StreamDescriptor stream : shuffled) {
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

}
