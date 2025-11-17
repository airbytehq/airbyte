/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.cdk.jdbc.JDBC_PROPERTY_PREFIX
import io.airbyte.cdk.read.CreateNoPartitions
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcPartitionFactory
import io.airbyte.cdk.read.JdbcSharedState
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** Concurrent JDBC implementation of [PartitionsCreatorFactory]. Support trigger based CDC only */
@Singleton
@Requires(property = MODE_PROPERTY, value = "concurrent_with_cdc")
class TriggerPartitionsCreatorFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    val partitionFactory: JdbcPartitionFactory<A, S, P>,
    val config: TriggerTableConfig,
    val deleteQuerier: DeleteQuerier,
) : PartitionsCreatorFactory {

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) return null
        val partition: P = partitionFactory.create(feedBootstrap) ?: return CreateNoPartitions
        return TriggerPartitionsCreator(partition, partitionFactory, config, deleteQuerier)
    }
}

private const val MODE_PROPERTY = "$JDBC_PROPERTY_PREFIX.mode"
