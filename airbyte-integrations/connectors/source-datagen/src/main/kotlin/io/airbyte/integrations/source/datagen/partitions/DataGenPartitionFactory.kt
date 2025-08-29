package io.airbyte.integrations.source.datagen.partitions

import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.StreamFeedBootstrap
import jakarta.inject.Singleton

@Singleton
class DataGenPartitionFactory (
    val concurrencyResource: ConcurrencyResource,
    val resourceAcquirer: ResourceAcquirer) : PartitionsCreatorFactory {
    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) {
            return null
        }
        return DataGenPartitionCreator(concurrencyResource, resourceAcquirer, feedBootstrap)
    }
}

@Singleton
class DataGenPartitionFactorySupplier<T : DataGenPartitionFactory> (val factory: T):
    PartitionsCreatorFactorySupplier<T> {
    override fun get(): T = factory
}
