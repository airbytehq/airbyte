/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

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
class SapHanaJdbcPartitionsCreatorFactory<
    A : JdbcSharedState,
    S : JdbcStreamState<A>,
    P : JdbcPartition<S>,
>(
    val partitionFactory: JdbcPartitionFactory<A, S, P>,
) : PartitionsCreatorFactory {

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) return null
        val partition: P = partitionFactory.create(feedBootstrap) ?: return CreateNoPartitions
        return SapHanaJdbcPartitionsCreator(partition, partitionFactory)
    }
}

private const val MODE_PROPERTY = "$JDBC_PROPERTY_PREFIX.mode"
