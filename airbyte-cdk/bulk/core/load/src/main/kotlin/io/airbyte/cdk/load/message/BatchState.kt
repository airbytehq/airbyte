/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

/**
 * Represents the state of a batch of records as it moves through processing. These are generic
 * stages for bookkeeping, which CDK interface devs can assign to processing stages as they see fit.
 * The only significant values are
 * - [BatchState.PERSISTED] Records will be considered recoverably persisted and checkpoints will be
 * acked to the orchestrator.
 * - [BatchState.COMPLETE] All per-batch processing is done. (Post-processing may still occur during
 * close-of-stream). Records are considered PERSISTED (ie, will be acked if not already). If all
 * records are COMPLETE, and end-of-stream has been read, the stream will be considered complete and
 * will be closed.
 * - All other values are for bookkeeping convenience only.
 */
enum class BatchState {
    PROCESSED, // records have been seen and transformed/formatted/validated (ie, create a part)
    STAGED, // staged locally or remotely-but-not-yet-complete (ie, partial multi-part upload)
    LOADED, // staged remotely but in a non-recoverable way (ie, a remote object in bulk load)
    PERSISTED, // recoverable (framework can ack), but not yet complete
    COMPLETE; // completely done; implies persisted (ie, framework can ack)

    fun isPersisted(): Boolean =
        when (this) {
            PERSISTED,
            COMPLETE -> true
            else -> false
        }
}
