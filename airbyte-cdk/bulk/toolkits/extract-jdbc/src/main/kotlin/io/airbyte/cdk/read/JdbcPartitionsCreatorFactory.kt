/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.jdbc.JDBC_PROPERTY_PREFIX
import io.airbyte.cdk.read.cdc.toCdcSharedState
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** Base class for JDBC implementations of [PartitionsCreatorFactory]. */
sealed class JdbcPartitionsCreatorFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    // TODO : Inject state required by CdcPartitionsCreator
    val partitionFactory: JdbcPartitionFactory<A, S, P>,
    val cdcContext: CdcContext,
    val initialCdcStateCreatorFactory: InitialCdcStateCreatorFactory
) : PartitionsCreatorFactory {

    override fun make(
        stateQuerier: StateQuerier,
        feed: Feed,
    ): PartitionsCreator {
        val opaqueStateValue: OpaqueStateValue? = stateQuerier.current(feed)
        val isGlobal = partitionFactory.sharedState.configuration.global
        return when (feed) {
            is Global ->
                when (isGlobal) {
                    true ->
                        CdcPartitionCreator(
                            partitionFactory.sharedState.toCdcSharedState(),
                            cdcContext,
                            initialCdcStateCreatorFactory.make(opaqueStateValue)
                        )
                    false -> CreateNoPartitions
                }
            is Stream -> {
                val partition: P? = partitionFactory.create(feed, opaqueStateValue)
                if (partition == null) {
                    CreateNoPartitions
                } else {
                    partitionsCreator(partition)
                }
            }
        }
    }

    abstract fun partitionsCreator(partition: P): JdbcPartitionsCreator<A, S, P>
}

/** Sequential JDBC implementation of [PartitionsCreatorFactory]. */
@Singleton
@Requires(property = MODE_PROPERTY, value = "sequential")
class JdbcSequentialPartitionsCreatorFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    partitionFactory: JdbcPartitionFactory<A, S, P>,
    cdcContext: CdcContext,
    initialCdcStateCreatorFactory: InitialCdcStateCreatorFactory
) :
    JdbcPartitionsCreatorFactory<A, S, P>(
        partitionFactory,
        cdcContext,
        initialCdcStateCreatorFactory
    ) {

    override fun partitionsCreator(partition: P): JdbcPartitionsCreator<A, S, P> =
        JdbcSequentialPartitionsCreator(partition, partitionFactory)
}

/** Concurrent JDBC implementation of [PartitionsCreatorFactory]. */
@Singleton
@Requires(property = MODE_PROPERTY, value = "concurrent")
class JdbcConcurrentPartitionsCreatorFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    partitionFactory: JdbcPartitionFactory<A, S, P>,
    cdcContext: CdcContext,
    initialCdcStateCreatorFactory: InitialCdcStateCreatorFactory
) :
    JdbcPartitionsCreatorFactory<A, S, P>(
        partitionFactory,
        cdcContext,
        initialCdcStateCreatorFactory
    ) {

    override fun partitionsCreator(partition: P): JdbcPartitionsCreator<A, S, P> =
        JdbcConcurrentPartitionsCreator(partition, partitionFactory)
}

private const val MODE_PROPERTY = "${JDBC_PROPERTY_PREFIX}.mode"
