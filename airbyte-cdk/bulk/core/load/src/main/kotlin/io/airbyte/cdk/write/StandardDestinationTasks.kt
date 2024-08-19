package io.airbyte.cdk.write

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.delay

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

class DefaultSetupTask(
    private val destination: StandardDestination
): Task() {
    override suspend fun execute() {
        destination.setup()

        DummyCatalog().streams.forEach { stream ->
            WorkQueue.instance.enqueue(DefaultOpenStreamTask(destination, stream))
        }
    }
}

class DefaultOpenStream(
    private val destination: StandardDestination,
    private val stream: Stream,
): DestinationTask<Unit>() {
    override val concurrency: Concurrency? = Concurrency("open")
    override suspend fun execute() {
        destination.openStreams.add(stream)
        destination.openStream(stream)
    }
}

class DefaultOpenStreamTask(
    private val destination: StandardDestination,
    private val stream: Stream,
): Task() {
    companion object {
        val N_ACCUMULATORS = 2
    }

    override val concurrency: Concurrency? = Task.Concurrency("open-stream", N_ACCUMULATORS * 2)

    override suspend fun execute() {
        destination.openStream(stream)

        (0..N_ACCUMULATORS).forEach {
            WorkQueue.instance.enqueue(DefaultAccumulateRecordsTask(destination, stream, it))
        }
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

class DefaultAccumulateRecordsTask(
    private val destination: StandardDestination,
    private val stream: Stream,
    private val shard: Int,
): Task() {
    override val concurrency: Concurrency? = Task.Concurrency("accumulate-records", 1)

    override suspend fun execute() {
        if (MessageQueue.instance.isStreamComplete(stream)) {
            return
        }

        val accumulator = destination.getRecordAccumulator(stream, shard)
        var batch: Batch? = null
        MessageQueue.instance.open(stream, shard).collect { record ->
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

        if (batch != null) {
            destination.openBatches.getOrPut(stream) { AtomicInteger(0) }.incrementAndGet()
            WorkQueue.instance.enqueue(DefaultProcessBatchTask(destination, stream, batch!!))
        }

        WorkQueue.instance.enqueue(this)
    }
}

class DefaultProcessBatch(
    private val destination: StandardDestination,
    private val stream: Stream,
    private val batch: Batch,
): DestinationTask<Batch?>() {
    override val concurrency: Concurrency? = Concurrency("batch")
    override suspend fun execute(): Batch? {
        return destination.processBatch(stream, batch)
    }
}

class DefaultProcessBatchTask(
    private val destination: StandardDestination,
    private val stream: Stream,
    private val batch: Batch,
): Task() {
    override val concurrency: Concurrency? = Task.Concurrency("process-batch", 1)

    override suspend fun execute() {
        val nextBatch = destination.processBatch(stream, batch)
        if (nextBatch != null) {
            WorkQueue.instance.enqueue(DefaultProcessBatchTask(destination, stream, nextBatch))
        } else {
            val remaining = destination.openBatches[stream]?.decrementAndGet()
            if (remaining == 0 && MessageQueue.instance.isStreamComplete(stream)) {
                WorkQueue.instance.enqueue(DefaultCloseStreamTask(destination, stream))
            }
        }
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

class DefaultCloseStreamTask(
    private val destination: StandardDestination,
    private val stream: Stream,
): Task() {
    companion object {
        val oncePerStream: ConcurrentHashMap<Stream, AtomicBoolean> = ConcurrentHashMap()
    }

    override val concurrency: Concurrency? = Task.Concurrency("close-stream", 1)

    override suspend fun execute() {
        if (oncePerStream.getOrPut(stream) { AtomicBoolean(false) }.getAndSet(true)) {
            return
        }
        while (!MessageQueue.instance.isStreamComplete(stream)) {
            delay(1000)
        }
        destination.closeStream(stream)
        destination.openStreams.remove(stream)
        WorkQueue.instance.enqueue(DefaultTeardownTask(destination))
    }
}

class DefaultTeardown(
    private val destination: StandardDestination
): DestinationTask<Unit>() {
    override suspend fun execute() {
        destination.teardown()
    }
}

class DefaultTeardownTask(
    private val destination: StandardDestination
): Task() {
    companion object {
        val once = AtomicBoolean(false)
    }

    override suspend fun execute() {
        if (once.getAndSet(true)) {
            return
        }
        while (!destination.openStreams.isEmpty()) {
            delay(1000)
        }
        destination.teardown()
    }
}
