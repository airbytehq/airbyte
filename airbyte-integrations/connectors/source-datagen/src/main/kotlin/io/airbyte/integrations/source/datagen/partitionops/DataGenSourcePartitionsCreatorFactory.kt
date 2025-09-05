/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.partitions

import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreator.TryAcquireResourcesStatus
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class DataGenSourcePartitionsCreatorFactory(val partitionFactory: DataGenSourcePartitionFactory) :
    PartitionsCreatorFactory {
    private val log = KotlinLogging.logger {}

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) {
            return null
        }

        val partition: DataGenSourcePartition =
            partitionFactory.create(feedBootstrap) ?: return CreateNoPartitions

        return DataGenPartitionsCreator(partition, partitionFactory)
    }
}

@Singleton
class DataGenSourcePartitionsCreatorFactorySupplier(
    val factory: DataGenSourcePartitionsCreatorFactory
) : PartitionsCreatorFactorySupplier<DataGenSourcePartitionsCreatorFactory> {
    override fun get() = factory
}

data object CreateNoPartitions : PartitionsCreator {
    override fun tryAcquireResources() = TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run(): List<PartitionReader> = listOf()

    override fun releaseResources() {}
}
