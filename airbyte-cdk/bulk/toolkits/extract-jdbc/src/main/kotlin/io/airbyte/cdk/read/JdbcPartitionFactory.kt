/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import io.micronaut.context.annotation.DefaultImplementation

/** Encapsulates database-specific logic turning [OpaqueStateValue] into [JdbcPartition]. */
@DefaultImplementation(DefaultJdbcPartitionFactory::class)
interface JdbcPartitionFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
> {

    /** The state shared by all partitions. Includes global resources. */
    val sharedState: A

    /** Get or create the [JdbcStreamState] for a [stream]. */
    fun streamState(stream: Stream): S

    /**
     * Deserializes [opaqueStateValue] and creates a [JdbcPartition] instance corresponding to all
     * remaining unread data in the [stream], if any; null otherwise.
     */
    fun create(stream: Stream, opaqueStateValue: OpaqueStateValue?): P?

    /** Subdivides the [unsplitPartition] by splitting at the [opaqueStateValues], if possible. */
    fun split(unsplitPartition: P, opaqueStateValues: List<OpaqueStateValue>): List<P>
}
