/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import io.airbyte.cdk.read.CreateNoPartitions
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

/**
 * Entry point of the READ operation: for each stream (table) feed, plans what is left to read given
 * the stream's current state and hands it to one [DynamoDbPartitionReader].
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
        val partition: DynamoDbPartition =
            DynamoDbPartition.plan(feedBootstrap, sharedState) ?: return CreateNoPartitions
        log.info {
            "Planned a scan of table '${partition.stream.name}'" +
                (partition.filter?.let { " with ${it.attribute} ${it.comparator} '${it.value}'" }
                    ?: "") +
                (partition.exclusiveStartKey?.let { " resuming after key $it" } ?: "")
        }
        return DynamoDbPartitionsCreator(partition, feedBootstrap, sharedState)
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
 * One partition per stream, read sequentially: no resources are needed to create it, the reader
 * acquires them.
 */
class DynamoDbPartitionsCreator(
    val partition: DynamoDbPartition,
    val feedBootstrap: StreamFeedBootstrap,
    val sharedState: DynamoDbSharedState,
) : PartitionsCreator {

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus =
        PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run(): List<PartitionReader> =
        listOf(DynamoDbPartitionReader(partition, feedBootstrap, sharedState))

    override fun releaseResources() {}
}
