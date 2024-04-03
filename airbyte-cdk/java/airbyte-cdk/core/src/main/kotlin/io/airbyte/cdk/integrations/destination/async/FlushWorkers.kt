/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.destination.async.buffers.BufferDequeue
import io.airbyte.cdk.integrations.destination.async.buffers.StreamAwareQueue
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.async.state.GlobalAsyncStateManager
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.scheduling.TaskExecutors
import io.micronaut.scheduling.TaskScheduler
import io.micronaut.scheduling.instrument.InstrumentedExecutorService
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.time.Duration
import java.util.Optional
import java.util.UUID
import java.util.concurrent.ExecutorService
import java.util.concurrent.ScheduledFuture
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.function.Consumer
import java.util.stream.Collectors

private val logger = KotlinLogging.logger {}

/**
 * Parallel flushing of Destination data.
 *
 * In combination with a [DestinationFlushFunction] and the [.workerPool], this class allows for
 * parallel data flushing.
 *
 * Parallelising is important as it 1) minimises Destination backpressure 2) minimises the effect of
 * IO pauses on Destination performance. The second point is particularly important since a majority
 * of Destination work is IO bound.
 *
 * The [.supervisorThread] assigns work to worker threads by looping over [.bufferDequeue] - a
 * dequeue interface over in-memory queues of [AirbyteMessage]. See [.retrieveWork] for assignment
 * logic.
 *
 * Within a worker thread, a worker best-effort reads a
 * [DestinationFlushFunction.optimalBatchSizeBytes] batch from the in-memory stream and calls
 * [DestinationFlushFunction.flush] on the returned data.
 *
 * Track the number of flush workers (and their size) that are currently running for a given stream.
 */
@SuppressFBWarnings(value = ["NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE"])
@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class FlushWorkers(
    private val globalAsyncStateManager: GlobalAsyncStateManager,
    private val bufferDequeue: BufferDequeue,
    private val destinationFlushFunction: DestinationFlushFunction,
    @Named("outputRecordCollector") private val outputRecordCollector: Consumer<AirbyteMessage>,
    @Named("destination-async-worker-pool-executor") private val workerPool: ExecutorService,
    @Named(TaskExecutors.SCHEDULED) private val taskScheduler: TaskScheduler,
    private val detectStreamToFlush: DetectStreamToFlush,
    private val runningFlushWorkers: RunningFlushWorkers,
    private val flushFailure: FlushFailure,
    private val airbyteFileUtils: AirbyteFileUtils,
) : AutoCloseable {
    private lateinit var supervisorFuture: ScheduledFuture<*>
    private lateinit var debugLoopFuture: ScheduledFuture<*>

    companion object {
        private const val SUPERVISOR_INITIAL_DELAY_SECS = 0L
        private const val SUPERVISOR_PERIOD_SECS = 1L
        private const val DEBUG_INITIAL_DELAY_SECS = 0L
        private const val DEBUG_PERIOD_SECS = 60L

        fun humanReadableFlushWorkerId(flushWorkerId: UUID): String {
            return flushWorkerId.toString().substring(0, 5)
        }
    }

    fun start() {
        logger.info { "Start async buffer supervisor" }
        supervisorFuture =
            taskScheduler.scheduleAtFixedRate(
                Duration.ofSeconds(SUPERVISOR_INITIAL_DELAY_SECS),
                Duration.ofSeconds(SUPERVISOR_PERIOD_SECS),
                this::retrieveWork,
            )
        debugLoopFuture =
            taskScheduler.scheduleAtFixedRate(
                Duration.ofSeconds(DEBUG_INITIAL_DELAY_SECS),
                Duration.ofSeconds(DEBUG_PERIOD_SECS),
                this::printWorkerInfo,
            )
    }

    private fun retrieveWork() {
        try {
            // This will put a new log line every second which is too much, sampling it doesn't
            // bring much value,
            // so it is set to debug
            logger.debug { "Retrieve Work -- Finding queues to flush" }
            val threadPoolExecutor =
                (workerPool as InstrumentedExecutorService).target as ThreadPoolExecutor
            var allocatableThreads =
                threadPoolExecutor.maximumPoolSize - threadPoolExecutor.activeCount

            while (allocatableThreads > 0) {
                val next: Optional<StreamDescriptor> = detectStreamToFlush.getNextStreamToFlush()

                if (next.isPresent) {
                    val desc = next.get()
                    val flushWorkerId = UUID.randomUUID()
                    runningFlushWorkers.trackFlushWorker(desc, flushWorkerId)
                    allocatableThreads--
                    flush(desc, flushWorkerId)
                } else {
                    break
                }
            }
        } catch (e: Exception) {
            logger.error(e) { "Flush worker error: " }
            flushFailure.propagateException(e)
        }
    }

    private fun printWorkerInfo() {
        val workerInfo = StringBuilder().append("[ASYNC WORKER INFO] ")

        val threadPoolExecutor = workerPool as ThreadPoolExecutor

        val queueSize = threadPoolExecutor.queue.size
        val activeCount = threadPoolExecutor.activeCount

        workerInfo.append("Pool queue size: $queueSize, Active threads: $activeCount")
        logger.info { workerInfo.toString() }
    }

    private fun flush(
        desc: StreamDescriptor,
        flushWorkerId: UUID,
    ) {
        workerPool.submit {
            logger.info {
                "Flush Worker (${humanReadableFlushWorkerId(
                        flushWorkerId,
                    )}) -- Worker picked up work."
            }
            try {
                logger.info {
                    "Flush Worker (${humanReadableFlushWorkerId(
                            flushWorkerId,
                        )}) -- Attempting to read from queue namespace: ${desc.namespace}, stream: ${desc.name}."
                }

                bufferDequeue.take(desc, destinationFlushFunction.optimalBatchSizeBytes).use { batch
                    ->
                    runningFlushWorkers.registerBatchSize(
                        desc,
                        flushWorkerId,
                        batch.sizeInBytes,
                    )
                    val stateIdToCount =
                        batch.batch
                            .stream()
                            .map(StreamAwareQueue.MessageWithMeta::stateId)
                            .collect(
                                Collectors.groupingBy(
                                    { stateId: Long -> stateId },
                                    Collectors.counting(),
                                ),
                            )
                    logger.info {
                        "Flush Worker (${humanReadableFlushWorkerId(
                                flushWorkerId,
                            )}) -- Batch contains: ${batch.batch.size} records, ${airbyteFileUtils.byteCountToDisplaySize(
                                batch.sizeInBytes,
                            )} bytes."
                    }

                    destinationFlushFunction.flush(
                        desc,
                        batch.batch
                            .stream()
                            .map(
                                StreamAwareQueue.MessageWithMeta::message,
                            ),
                    )
                    batch.flushStates(stateIdToCount, outputRecordCollector)
                }
                logger.info {
                    "Flush Worker (${humanReadableFlushWorkerId(
                            flushWorkerId,
                        )}) -- Worker finished flushing. Current queue size: ${bufferDequeue.getQueueSizeInRecords(
                            desc,
                        ).orElseThrow()}"
                }
            } catch (e: Exception) {
                logger.error(e) {
                    "Flush Worker (${humanReadableFlushWorkerId(
                            flushWorkerId,
                        )}) -- flush worker error: "
                }
                flushFailure.propagateException(e)
                throw RuntimeException(e)
            } finally {
                runningFlushWorkers.completeFlushWorker(desc, flushWorkerId)
            }
        }
    }

    @Throws(Exception::class)
    override fun close() {
        logger.info { "Closing flush workers -- waiting for all buffers to flush" }
        detectStreamToFlush.flushAllStreams.set(true)
        // wait for all buffers to be flushed.
        while (true) {
            val streamDescriptorToRemainingRecords =
                bufferDequeue
                    .getBufferedStreams()
                    .stream()
                    .collect(
                        Collectors.toMap(
                            { desc: StreamDescriptor -> desc },
                            { desc: StreamDescriptor? ->
                                bufferDequeue
                                    .getQueueSizeInRecords(
                                        desc!!,
                                    )
                                    .orElseThrow()
                            },
                        ),
                    )

            val anyRecordsLeft =
                streamDescriptorToRemainingRecords.values.stream().anyMatch { size: Long ->
                    size > 0
                }

            if (!anyRecordsLeft) {
                break
            }

            val workerInfo =
                StringBuilder()
                    .append(
                        "REMAINING_BUFFERS_INFO",
                    )
                    .append(System.lineSeparator())
            streamDescriptorToRemainingRecords.entries
                .stream()
                .filter { entry: Map.Entry<StreamDescriptor, Long> -> entry.value > 0 }
                .forEach { entry: Map.Entry<StreamDescriptor, Long> ->
                    workerInfo.append(
                        String.format(
                            "  Namespace: %s Stream: %s -- remaining records: %d",
                            entry.key.namespace,
                            entry.key.name,
                            entry.value,
                        ),
                    )
                }
            logger.info { workerInfo.toString() }
            logger.info { "Waiting for all streams to flush." }
            Thread.sleep(1000)
        }
        logger.info { "Closing flush workers -- all buffers flushed" }

        // before shutting, flush all state.
        globalAsyncStateManager.flushStates(outputRecordCollector)

        supervisorFuture.cancel(true)
        logger.info { "Closing flush workers -- supervisor shut down" }

        logger.info { "Closing flush workers -- Starting worker pool shutdown.." }
        workerPool.shutdown()
        while (!workerPool.awaitTermination(5L, TimeUnit.MINUTES)) {
            logger.info { "Waiting for flush workers to shut down" }
        }
        logger.info { "Closing flush workers  -- workers shut down" }

        debugLoopFuture.cancel(true)
    }
}
