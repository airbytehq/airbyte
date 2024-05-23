/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Clock
import java.time.Instant
import java.util.Optional
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.math.min

private val logger = KotlinLogging.logger {}

/** This class finds the best, next stream to flush. */
class DetectStreamToFlush
@VisibleForTesting
internal constructor(
    private val bufferDequeue: BufferDequeue,
    private val runningFlushWorkers: RunningFlushWorkers,
    private val isClosing: AtomicBoolean,
    private val flusher: DestinationFlushFunction,
    private val nowProvider: Clock,
) {
    private val latestFlushTimeMsPerStream: ConcurrentMap<StreamDescriptor, Long> =
        ConcurrentHashMap()

    constructor(
        bufferDequeue: BufferDequeue,
        runningFlushWorkers: RunningFlushWorkers,
        isClosing: AtomicBoolean,
        flusher: DestinationFlushFunction,
    ) : this(bufferDequeue, runningFlushWorkers, isClosing, flusher, Clock.systemUTC())

    val nextStreamToFlush: Optional<StreamDescriptor>
        /**
         * Get the best, next stream that is ready to be flushed.
         *
         * @return best, next stream to flush. If no stream is ready to be flushed, return empty.
         */
        get() = getNextStreamToFlush(computeQueueThreshold())

    /**
     * We have a minimum threshold for the size of a queue before we will flush it. The threshold
     * helps us avoid uploading small amounts of data at a time, which is really resource
     * inefficient. Depending on certain conditions, we dynamically adjust this threshold.
     *
     * Rules:
     * * default - By default the, the threshold is a set at a constant:
     * QUEUE_FLUSH_THRESHOLD_BYTES.
     * * memory pressure - If we are getting close to maxing out available memory, we reduce it to
     * zero. This helps in the case where there are a lot of streams, so total memory usage is high,
     * but each individual queue isn't that large.
     * * closing - If the Flush Worker is closing, we reduce it to zero. We close when all records
     * have been added to the queue, at which point, our goal is to flush out any non-empty queues.
     *
     * @return based on the conditions, the threshold in bytes.
     */
    @VisibleForTesting
    fun computeQueueThreshold(): Long {
        val isBuffer90Full =
            EAGER_FLUSH_THRESHOLD <=
                bufferDequeue.totalGlobalQueueSizeBytes.toDouble() / bufferDequeue.maxQueueSizeBytes
        // when we are closing or queues are very full, flush regardless of how few items are in the
        // queue.
        return if (isClosing.get() || isBuffer90Full) 0 else flusher.queueFlushThresholdBytes
    }

    // todo (cgardens) - improve prioritization by getting a better estimate of how much data
    // running
    // workers will process. we have access to their batch sizes after all!

    /**
     * Iterates over streams until it finds one that is ready to flush. Streams are ordered by
     * priority. Return an empty optional if no streams are ready.
     *
     * A stream is ready to flush if it either meets a size threshold or a time threshold. See
     * [.isSizeTriggered] and [.isTimeTriggered] for details on these triggers.
     *
     * @param queueSizeThresholdBytes
     * - the size threshold to use for determining if a stream is ready to flush.
     * @return the next stream to flush. if no stream is ready to flush, empty.
     */
    @VisibleForTesting
    fun getNextStreamToFlush(queueSizeThresholdBytes: Long): Optional<StreamDescriptor> {
        for (stream in orderStreamsByPriority(bufferDequeue.bufferedStreams)) {
            val latestFlushTimeMs =
                latestFlushTimeMsPerStream.computeIfAbsent(
                    stream,
                ) { _: StreamDescriptor ->
                    nowProvider.millis()
                }
            val isTimeTriggeredResult = isTimeTriggered(latestFlushTimeMs)
            val isSizeTriggeredResult = isSizeTriggered(stream, queueSizeThresholdBytes)

            val debugString =
                "trigger info: ${stream.namespace} - ${stream.name}, " +
                    "${isTimeTriggeredResult.second} , ${isSizeTriggeredResult.second}"
            logger.debug { "computed: $debugString" }

            if (isSizeTriggeredResult.first || isTimeTriggeredResult.first) {
                logger.info { "flushing: $debugString" }
                latestFlushTimeMsPerStream[stream] = nowProvider.millis()
                return Optional.of(stream)
            }
        }
        return Optional.empty()
    }

    /**
     * The time trigger is based on the last time a record was added to the queue. We don't want
     * records to sit forever, even if the queue is not that full (bad for time to value for users).
     * Also, the more time passes since a record was added, the less likely another record is coming
     * (caveat is CDC where it's random).
     *
     * This method also returns debug string with info that about the computation. We do it this
     * way, so that the debug info that is printed is exactly what is used in the computation.
     *
     * @param latestFlushTimeMs latestFlushTimeMs
     * @return is time triggered and a debug string
     */
    @VisibleForTesting
    fun isTimeTriggered(latestFlushTimeMs: Long): Pair<Boolean, String> {
        val timeSinceLastFlushMs = nowProvider.millis() - latestFlushTimeMs
        val isTimeTriggered = timeSinceLastFlushMs >= MAX_TIME_BETWEEN_FLUSH_MS
        val debugString = "time trigger: $isTimeTriggered"

        return Pair(isTimeTriggered, debugString)
    }

    /**
     * For the size threshold, the size of the data in the queue is compared to the threshold that
     * is passed into this method.
     *
     * One caveat, is that if that stream already has a worker running, we "penalize" its size. We
     * do this by computing what the size of the queue would be after the running workers for that
     * queue complete. This is based on a dumb estimate of how much data a worker can process. There
     * is an opportunity for optimization here, by being smarter about predicting how much data a
     * running worker is likely to process.
     *
     * This method also returns debug string with info that about the computation. We do it this
     * way, so that the debug info that is printed is exactly what is used in the computation.
     *
     * @param stream stream
     * @param queueSizeThresholdBytes min size threshold to determine if a queue is ready to flush
     * @return is size triggered and a debug string
     */
    @VisibleForTesting
    fun isSizeTriggered(
        stream: StreamDescriptor,
        queueSizeThresholdBytes: Long,
    ): Pair<Boolean, String> {
        val currentQueueSize = bufferDequeue.getQueueSizeBytes(stream).orElseThrow()
        val sizeOfRunningWorkersEstimate = estimateSizeOfRunningWorkers(stream, currentQueueSize)
        val queueSizeAfterRunningWorkers = currentQueueSize - sizeOfRunningWorkersEstimate
        val isSizeTriggered = queueSizeAfterRunningWorkers > queueSizeThresholdBytes

        val debugString =
            "size trigger: $isSizeTriggered " +
                "current threshold b: ${AirbyteFileUtils.byteCountToDisplaySize(queueSizeThresholdBytes)}, " +
                "queue size b: ${AirbyteFileUtils.byteCountToDisplaySize(currentQueueSize)}, " +
                "penalty b: ${AirbyteFileUtils.byteCountToDisplaySize(sizeOfRunningWorkersEstimate)}, " +
                "after penalty b: ${AirbyteFileUtils.byteCountToDisplaySize(queueSizeAfterRunningWorkers)}"

        return Pair(isSizeTriggered, debugString)
    }

    /**
     * For a stream, determines how many bytes will be processed by CURRENTLY running workers. For
     * the purpose of this calculation, workers can be in one of two states. First, they can have a
     * batch, in which case, we can read the size in bytes from the batch to know how many records
     * that batch will pull of the queue. Second, it might not have a batch yet, in which case, we
     * assume the min of bytes in the queue or the optimal flush size.
     *
     * @param stream stream
     * @return estimate of records remaining to be process
     */
    @VisibleForTesting
    fun estimateSizeOfRunningWorkers(
        stream: StreamDescriptor,
        currentQueueSize: Long,
    ): Long {
        val runningWorkerBatchesSizes =
            runningFlushWorkers.getSizesOfRunningWorkerBatches(
                stream,
            )
        val workersWithBatchesSize =
            runningWorkerBatchesSizes
                .filter { obj: Optional<Long> -> obj.isPresent }
                .sumOf { obj: Optional<Long> -> obj.get() }
        val workersWithoutBatchesCount =
            runningWorkerBatchesSizes.count { obj: Optional<Long> -> obj.isEmpty }
        val workersWithoutBatchesSizeEstimate =
            (min(
                    flusher.optimalBatchSizeBytes.toDouble(),
                    currentQueueSize.toDouble(),
                ) * workersWithoutBatchesCount)
                .toLong()
        return (workersWithBatchesSize + workersWithoutBatchesSizeEstimate)
    }

    // todo (cgardens) - perf test whether it would make sense to flip 1 & 2.

    /**
     * Sort stream descriptors in order of priority with which we would want to flush them.
     *
     * Priority is in the following order:
     * * 1. size in queue (descending)
     * * 2. time since last record (ascending)
     * * 3. alphabetical by namespace + stream name.
     *
     * In other words, move the biggest queues first, because they are most likely to use available
     * resources optimally. Then get rid of old stuff (time to value for the user and, generally, as
     * the age of the last record grows, the likelihood of getting any more records from that stream
     * decreases, so by flushing them, we can totally complete that stream). Finally, tertiary sort
     * by name so the order is deterministic.
     *
     * @param streams streams to sort.
     * @return streams sorted by priority.
     */
    @VisibleForTesting
    fun orderStreamsByPriority(streams: Set<StreamDescriptor>): List<StreamDescriptor> {
        // eagerly pull attributes so that values are consistent throughout comparison
        val sdToQueueSize =
            streams.associateWith { streamDescriptor: StreamDescriptor ->
                bufferDequeue.getQueueSizeBytes(
                    streamDescriptor,
                )
            }

        val sdToTimeOfLastRecord =
            streams.associateWith { streamDescriptor: StreamDescriptor ->
                bufferDequeue.getTimeOfLastRecord(
                    streamDescriptor,
                )
            }
        return streams
            .sortedWith(
                Comparator.comparing(
                        { s: StreamDescriptor -> sdToQueueSize[s]!!.orElseThrow() },
                        Comparator.reverseOrder(),
                    ) // if no time is present, it suggests the queue has no records. set MAX time
                    // as a sentinel value to
                    // represent no records.
                    .thenComparing { s: StreamDescriptor ->
                        sdToTimeOfLastRecord[s]!!.orElse(Instant.MAX)
                    }
                    .thenComparing { s: StreamDescriptor -> s.namespace + s.name },
            )
            .toList()
    }

    companion object {
        private const val EAGER_FLUSH_THRESHOLD = 0.90
        private const val MAX_TIME_BETWEEN_FLUSH_MS = (5 * 60 * 1000).toLong()
    }
}
