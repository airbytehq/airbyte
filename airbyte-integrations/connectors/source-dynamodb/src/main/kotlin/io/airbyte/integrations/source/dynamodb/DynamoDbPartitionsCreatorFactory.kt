/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import io.airbyte.cdk.read.CreateNoPartitions
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.StreamFeedBootstrap
import jakarta.inject.Singleton

/**
 * Entry point of the READ operation: for each stream (table) feed, plans what is left to read given
 * the stream's current state and the progress made in this run, and hands every unfinished segment
 * of the table to its own [DynamoDbPartitionReader].
 *
 * This connector has no `Global` feed (no CDC), so anything else gets [CreateNoPartitions].
 */
@Singleton
class DynamoDbPartitionsCreatorFactory(
    val sharedState: DynamoDbSharedState,
) : PartitionsCreatorFactory {

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) {
            return CreateNoPartitions
        }
        return DynamoDbPartitionsCreator(feedBootstrap, sharedState)
    }
}

/** [io.airbyte.cdk.read.ReadOperation] looks up the suppliers, not the factories. */
@Singleton
class DynamoDbPartitionsCreatorFactorySupplier(
    val factory: DynamoDbPartitionsCreatorFactory,
) : PartitionsCreatorFactorySupplier<DynamoDbPartitionsCreatorFactory> {
    override fun get(): DynamoDbPartitionsCreatorFactory = factory
}

/**
 * One partition per unfinished segment of the table, in segment order; no resources are needed to
 * plan them (one `DescribeTable` on the table's first round), the readers acquire theirs. An empty
 * list ends the feed.
 */
class DynamoDbPartitionsCreator(
    val feedBootstrap: StreamFeedBootstrap,
    val sharedState: DynamoDbSharedState,
) : PartitionsCreator {

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus =
        PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run(): List<PartitionReader> =
        when (val plan: DynamoDbReadPlan = DynamoDbPartition.plan(feedBootstrap, sharedState)) {
            is DynamoDbReadPlan.Done -> emptyList()
            is DynamoDbReadPlan.Finalize ->
                listOf(
                    DynamoDbTerminalStateReader(plan.stream, plan.scan, plan.cursor, feedBootstrap)
                )
            is DynamoDbReadPlan.Scan ->
                plan.partitions.map { DynamoDbPartitionReader(it, feedBootstrap, sharedState) }
        }

    override fun releaseResources() {}
}
