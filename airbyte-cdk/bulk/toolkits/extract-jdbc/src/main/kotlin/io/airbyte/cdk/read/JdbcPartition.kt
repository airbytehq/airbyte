/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue

/**
 * Encapsulates database-specific aspects relating to a JDBC stream partition, consumed by
 * [JdbcPartitionReader] and friends.
 */
interface JdbcPartition<S : JdbcStreamState<*>> {

    /** The partition's stream's transient state, including parameters like fetchSize, etc. */
    val streamState: S

    /** Query which produces all records in the partition in no particular order. */
    val nonResumableQuery: SelectQuery

    /** State value to emit when the partition is read in its entirety. */
    val completeState: OpaqueStateValue

    /** Query which samples records in the partition at the rate of 2^-[sampleRateInvPow2]. */
    fun samplingQuery(sampleRateInvPow2: Int): SelectQuery

    /** Tries to acquire resources for [JdbcPartitionsCreator]. */
    fun tryAcquireResourcesForCreator(): JdbcPartitionsCreator.AcquiredResources? =
        // Acquire global resources by default.
        streamState.sharedState.tryAcquireResourcesForCreator()

    /** Tries to acquire resources for [JdbcPartitionReader]. */
    fun tryAcquireResourcesForReader(): JdbcPartitionReader.AcquiredResources? =
        // Acquire global resources by default.
        streamState.sharedState.tryAcquireResourcesForReader()
}

/** A [JdbcPartition] which can be subdivided. */
interface JdbcSplittablePartition<S : JdbcStreamState<*>> : JdbcPartition<S> {

    /** Query which produces a subset of records at the beginning of the partition. */
    fun resumableQuery(limit: Long): SelectQuery

    /** State value to emit when the partition is read up to (and including) [lastRecord]. */
    fun incompleteState(lastRecord: ObjectNode): OpaqueStateValue
}

/** A [JdbcPartition] which allows cursor-based incremental reads. */
interface JdbcCursorPartition<S : JdbcStreamState<*>> : JdbcPartition<S> {

    /** Query which produces the current maximum cursor value in the stream. */
    val cursorUpperBoundQuery: SelectQuery
}
