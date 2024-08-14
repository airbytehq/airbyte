package io.airbyte.cdk.write

/**
 * Represents an accumulated batch of records in some stage of processing.
 *
 * Emitted by the record accumulator per batch accumulated. Handled by
 * the batch processor, which may advanced the state and yield a new batch.
 *
 * If persisted is true, the framework will close state for the accumulated messages.
 */
open class Batch(
    val name: String,
    val persisted: Boolean = false
)
