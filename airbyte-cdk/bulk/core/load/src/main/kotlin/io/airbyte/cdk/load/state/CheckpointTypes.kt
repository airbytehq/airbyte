/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.DestinationStream

/**
 * These types are copied from the legacy CDK for compatibility.
 * TODO: Reconsider these abstractions as the modern dataflow architecture evolves.
 */

/** Represents the ordering of a checkpoint. */
@JvmInline value class CheckpointIndex(val value: Int)

/** Unique identifier for a checkpoint. */
@JvmInline value class CheckpointId(val value: String)

/** Composite key combining checkpoint index and id. Ordered by index only. */
data class CheckpointKey(
    val checkpointIndex: CheckpointIndex,
    val checkpointId: CheckpointId,
) : Comparable<CheckpointKey> {
    override fun compareTo(other: CheckpointKey): Int {
        return this.checkpointIndex.value - other.checkpointIndex.value
    }
}

/** Tracks record and byte counts for a checkpoint. */
data class CheckpointValue(
    val records: Long,
    val serializedBytes: Long,
    val rejectedRecords: Long = 0,
) {
    operator fun plus(other: CheckpointValue): CheckpointValue {
        return CheckpointValue(
            records = records + other.records,
            serializedBytes = serializedBytes + other.serializedBytes,
            rejectedRecords = rejectedRecords + other.rejectedRecords,
        )
    }

    override fun equals(other: Any?): Boolean {
        if (other != null && other is CheckpointValue) {
            return this.records == other.records &&
                this.serializedBytes == other.serializedBytes &&
                this.rejectedRecords == other.rejectedRecords
        }
        return false
    }
}

/** Result of stream processing. */
sealed interface StreamResult

data class StreamProcessingFailed(val streamException: Exception) : StreamResult

data object StreamProcessingSucceeded : StreamResult

/** Result of destination processing. */
sealed interface DestinationResult

data object DestinationSuccess : DestinationResult

data class DestinationFailure(
    val cause: Exception,
    val streamResults: Map<DestinationStream.Descriptor, StreamResult>
) : DestinationResult