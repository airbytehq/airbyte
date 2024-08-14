package io.airbyte.cdk.write

abstract class StandardDestination {

    // Called once before anything else
    open fun setup() {}

    // Called once per stream before any records are processed
    open fun openStream(stream: Stream) {}

    // Called continuously until end of stream
    abstract fun accumulateRecords(
        stream: Stream,
        accumulatorId: Int,
        records: Iterable<DestinationRecord>,
        endOfStream: Boolean = false,
        forceFlush: Boolean = false
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
