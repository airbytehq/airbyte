package io.airbyte.cdk.write

/**
 * These tasks together are sufficient to drive the StandardDestination lifecycle.
 */

fun taskList(d: StandardDestination) = TaskList(listOf(
    DefaultSetup(d),
    ForEachStream { stream -> TaskList(listOf(
            DefaultOpenStream(d, stream),
            Replicated(2) { shard ->
                UntilStreamComplete(stream) {
                    Do { DefaultAccumulateRecords(d, stream, shard) }
                }.mapValue { batch: Batch? ->
                    if (batch != null) {
                        IterateUntilNull(batch) { nextBatch ->
                            DefaultProcessBatch(d, stream, nextBatch)
                        }
                    } else {
                        Return(null)
                    }
                }
            }.mapValue { _ -> Noop() },
            DefaultCloseStream(d, stream),
        ))
    },
    DefaultTeardown(d),
    Done()
))

class DefaultSetup(
    private val destination: StandardDestination
): DestinationTask<Unit>() {
    override suspend fun execute() {
        destination.setup()
    }
}

class DefaultOpenStream(
    private val destination: StandardDestination,
    private val stream: Stream,
): DestinationTask<Unit>() {
    override val concurrency: Concurrency? = Concurrency("open")
    override suspend fun execute() {
        destination.openStream(stream)
    }
}

class DefaultAccumulateRecords(
    private val destination: StandardDestination,
    private val stream: Stream,
    private val shard: Int,
): DestinationTask<Batch?>() {
    override val concurrency: Concurrency? = Concurrency("accumulate")

    private val queue = MessageQueue.instance

    override suspend fun execute(): Batch? {
        val accumulator = destination.getRecordAccumulator(stream, shard)
        var batch: Batch? = null
        queue.open(stream, shard).collect { record ->
            if (record == null) { // Timeout, or past end-of-stream/chunk
                return@collect
            }
            when (record) {
                is DestinationMessage.DestinationRecord ->
                    batch = accumulator.invoke(record)
                is DestinationMessage.EndOfStream ->
                    batch = destination.flush(stream, endOfStream = true)
            }
            if (batch != null) {
                return@collect
            }
        }

        return batch
    }
}

class DefaultProcessBatch(
    private val destination: StandardDestination,
    val stream: Stream,
    private val batch: Batch,
): DestinationTask<Batch?>() {
    override val concurrency: Concurrency? = Concurrency("batch")
    override suspend fun execute(): Batch? {
        return destination.processBatch(stream, batch)
    }
}

class DefaultCloseStream(
    private val destination: StandardDestination,
    private val stream: Stream,
): DestinationTask<Unit>() {
    override val concurrency: Concurrency? = Concurrency("close")
    override suspend fun execute() {
        destination.closeStream(stream)
    }
}

class DefaultTeardown(
    private val destination: StandardDestination
): DestinationTask<Unit>() {
    override suspend fun execute() {
        destination.teardown()
    }
}
