package io.airbyte.cdk.write

import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.flow.fold
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.runInterruptible

/**
 * These tasks together are sufficient to drive the StandardDestination lifecycle.
 */

class DefaultSetup(
    private val destination: StandardDestination
): DestinationTask() {
    override suspend fun execute(): DestinationTask {
        destination.setup()
        return ForEachStream {
            Incrementing("open-stream") {
                DefaultOpenStream(stream = it, destination)
            }
        }
    }
}

class DefaultOpenStream(
    override val stream: Stream,
    private val destination: StandardDestination
): DestinationTask(), PerStream {
    override val concurrency: Concurrency? = Concurrency("open")
    override suspend fun execute(): DestinationTask {
        destination.openStream(stream)
        return ForEachAvailable {
            DefaultAccumulateRecords(stream, taskId = it, destination)
        }
    }
}

class DefaultAccumulateRecords(
    override val stream: Stream,
    private val taskId: Int,
    private val destination: StandardDestination
): DestinationTask(), RecordConsumer, PerStream {
    override val concurrency: Concurrency? = Concurrency("accumulate")

    private val queue = MessageQueue.instance

    val log = KotlinLogging.logger {}

    override suspend fun execute(): DestinationTask {
        val batch =
            queue.open(stream, taskId).fold(null as Batch?) { _, record ->
                val result = when (record) {
                    is DestinationMessage.DestinationRecord -> {
                        log.info { "task: Accumulating record $record" }
                        destination.accumulateRecords(
                            stream, taskId, listOf(record), false, false
                        )
                    }
                    is DestinationMessage.EndOfStream -> {
                        log.info { "task: End of stream $stream" }
                        destination.accumulateRecords(
                            stream, taskId, emptyList(), true, false
                        )
                    }
                    is DestinationMessage.TimeOut -> {
                        log.info { "task: Timeout on stream $stream" }
                        null
                    }
                }
                if (result != null) {
                    return@fold result
                } else {
                    null
                }
            }

        // Currently the task will be re-enqueued automatically until EOS
        if (batch != null) {
            return Incrementing("batch:$stream") {
                DefaultProcessBatch(stream, batch, destination)
            }
        } else {
            return Noop()
        }
    }
}

class DefaultProcessBatch(
    override val stream: Stream,
    private val batch: Batch,
    private val destination: StandardDestination
): DestinationTask(), PerStream {
    override val concurrency: Concurrency? = Concurrency("batch")
    override suspend fun execute(): DestinationTask {
        val nextBatch = destination.processBatch(stream, batch)
        if (nextBatch != null) {
            return DefaultProcessBatch(stream, nextBatch, destination)
        } else {
            return Decrementing("batch:$stream") {
                ExactlyOnce("eos:$stream") {
                    WhenStreamComplete(stream) {
                        WhenAllComplete("batch:$stream") {
                            DefaultCloseStream(stream, destination)
                        }
                    }
                }
            }
        }
    }
}

class DefaultCloseStream(
    override val stream: Stream,
    private val destination: StandardDestination
): DestinationTask(), PerStream {
    override val concurrency: Concurrency? = Concurrency("close")
    override suspend fun execute(): DestinationTask {
        destination.closeStream(stream)
        return Decrementing("open-stream") {
                ExactlyOnce("teardown") {
                    WhenAllComplete("open-stream") {
                        DefaultTeardown(destination)
                    }
                }
            }
    }
}

class DefaultTeardown(
    private val destination: StandardDestination
): DestinationTask() {
    override suspend fun execute(): DestinationTask {
        destination.teardown()
        return Done()
    }
}
