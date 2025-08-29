package io.airbyte.integrations.source.datagen.partitions

import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator.TryAcquireResourcesStatus
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.StreamFeedBootstrap
import jakarta.inject.Singleton

@Singleton
class DataGenPartitionReader (val resourceAcquirer: ResourceAcquirer, val feedBootstrap: StreamFeedBootstrap) : PartitionReader {
    override fun tryAcquireResources() = PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run() {
        TODO("Not yet implemented")
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        TODO("Not yet implemented")

    }

    override fun releaseResources() {
        TODO("Not yet implemented")
    }
}
