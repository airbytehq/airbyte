package io.airbyte.integrations.source.datagen.partitionops

import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSourcePartition
import jakarta.inject.Singleton

@Singleton
class DataGenSourcePartitionCreatorFactory(
    val partitionFactory: DataGenSourcePartitionFactory
) : PartitionsCreatorFactory {
    override fun make(feedBootstrap: FeedBootstrap<*>): DataGenPartitionCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) {
            return null
        }
        val partition: DataGenSourcePartition =
            partitionFactory.create(feedBootstrap) ?: return null
        return DataGenPartitionCreator(partition, partitionFactory)
    }
}

@Singleton
class DataGenSourcePartitionCreatorFactorySupplier<T : DataGenSourcePartitionCreatorFactory> (val factory: T):
    PartitionsCreatorFactorySupplier<T> {
    override fun get(): T = factory
}
