package io.airbyte.cdk.write

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger
import org.apache.mina.util.ConcurrentHashSet

abstract class StandardDestination {
    val openStreams: ConcurrentHashSet<Stream> = ConcurrentHashSet()
    val openBatches: ConcurrentHashMap<Stream, AtomicInteger> = ConcurrentHashMap()

    // Called once before anything else
    open fun setup() {}

    // Called once per stream before any records are processed
    open fun openStream(stream: Stream) {}

    // Called periodically as data is available
    // to get an accumulator that will be called
    // continously per record until EOS or the data
    // are no longer available.
    abstract fun getRecordAccumulator(
        stream: Stream,
        shard: Int
    ): (DestinationMessage.DestinationRecord) -> Batch?

    // Called at least once, at the end of stream.
    // May be called earlier by the framework, indicating
    // a forced flush point (eg, every five minutes).
    abstract fun flush(
        stream: Stream,
        endOfStream: Boolean = false
    ): Batch?

    // Called once per any method that returns a
    // non-null batch (including itself).
    open fun processBatch(
        stream: Stream,
        batch: Batch
    ): Batch? = null

    // Called once per stream after the last
    // batch is processed
    open fun closeStream(
        stream: Stream,
        succeeded: Boolean = true
    ) {}

    // Called once at the end of the job
    open fun teardown(succeeded: Boolean = true) {}

    // (Not implemented yet.)
    // Respond to acknowledged destination state,
    // possibly yielding a batch to process
    // (ie, if you want to hold off on processing
    // a batch before the ack, persist its meta-
    // data in the state, and then yield it here)
    open fun handleDestinationState(
        state: DestinationState,
        batch: Batch
    ): Batch? = null
}
