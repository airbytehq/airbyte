package io.airbyte.cdk.write

/**
 * These tasks together are sufficient to drive the StandardDestination lifecycle.
 */

class DefaultSetup(
    private val destination: StandardDestination
): DestinationTask() {
    override fun execute(): DestinationTask {
        destination.setup()
        return ForEachStream {
            DefaultOpenStream(stream = it, destination)
        }
    }
}

class DefaultOpenStream(
    override val stream: Stream,
    private val destination: StandardDestination
): DestinationTask(), PerStream {
    override val concurrency: Concurrency? = Concurrency("open")
    override fun execute(): DestinationTask {
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

    override var payload: Iterable<DestinationRecord>? = null
    override var endOfStream: Boolean = false
    override var forceFlush: Boolean = false

    override fun execute(): DestinationTask {
        val batch = destination.accumulateRecords(
            stream, taskId, payload!!, endOfStream, forceFlush)
        if (batch != null) {
            return Incrementing("batch:$stream") {
                DefaultProcessBatch(stream, batch, destination)
            }
        } else {
            return this
        }
    }
}

class DefaultProcessBatch(
    override val stream: Stream,
    private val batch: Batch,
    private val destination: StandardDestination
): DestinationTask(), PerStream {
    override val concurrency: Concurrency? = Concurrency("batch")
    override fun execute(): DestinationTask {
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
    override fun execute(): DestinationTask {
        destination.closeStream(stream)
        return DefaultTeardown(destination)
    }
}

class DefaultTeardown(
    private val destination: StandardDestination
): DestinationTask() {
    override fun execute(): DestinationTask {
        destination.teardown()
        return Done()
    }
}
