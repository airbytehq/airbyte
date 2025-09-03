package io.airbyte.integrations.source.datagen.partitions

import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator.TryAcquireResourcesStatus
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.ResourceType.RESOURCE_DB_CONNECTION
import io.airbyte.cdk.read.ResourceType.RESOURCE_OUTPUT_SOCKET
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.generatePartitionId
import io.airbyte.cdk.util.Jsons
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicReference

@Singleton
class DataGenPartitionReader (val resourceAcquirer: ResourceAcquirer, val feedBootstrap: StreamFeedBootstrap) : PartitionReader {
    lateinit var outputMessageRouter: OutputMessageRouter
    // dont need this rn cuz just doing 1 partition
    // protected var partitionId: String = generatePartitionId(4)
    protected var partitionId: String = "0"
    interface AcquiredResource : AutoCloseable {
        val resource: Resource.Acquired?
    }
    private val acquiredResources = AtomicReference<Map<ResourceType,AcquiredResource>>()

    override fun tryAcquireResources() : PartitionReader.TryAcquireResourcesStatus{
        val resourceType =
            when (feedBootstrap.dataChannelMedium) {
                DataChannelMedium.STDIO -> listOf(RESOURCE_DB_CONNECTION)
                DataChannelMedium.SOCKET ->
                    listOf(RESOURCE_DB_CONNECTION, RESOURCE_OUTPUT_SOCKET)
            }
        fun tryAcquireResources(
            resourcesType: List<ResourceType>
        ): Map<ResourceType, AcquiredResource>? {
            val resources: Map<ResourceType, Resource.Acquired>? =
                resourceAcquirer.tryAcquire(resourcesType)
            return resources
                ?.map {
                    it.key to
                        object : AcquiredResource {
                            override val resource: Resource.Acquired = it.value
                            override fun close() {
                                resource.close()
                            }
                        }
                }
                ?.toMap()
        }
        val resources: Map<ResourceType, AcquiredResource> =
            tryAcquireResources(resourceType)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER

        acquiredResources.set(resources)
        // what does this do? and do i need it
        outputMessageRouter =
            OutputMessageRouter(
                feedBootstrap.dataChannelMedium,
                feedBootstrap.dataChannelFormat,
                feedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                feedBootstrap,
                acquiredResources
                    .get()
                    .filter { it.value.resource != null }
                    .map { it.key to it.value.resource!! }
                    .toMap()
            )
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {

    }

    override fun checkpoint(): PartitionReadCheckpoint {
//        return PartitionReadCheckpoint(
//            feedBootstrap.currentState ?: Jsons.objectNode(),
//            (acquiredResources.get().size).toLong(),
//            when (feedBootstrap.dataChannelMedium) {
//                DataChannelMedium.STDIO -> null
//                DataChannelMedium.SOCKET -> partitionId
//            }
//        )
        throw RuntimeException("cannot checkpoint datagen")
    }

    override fun releaseResources() {
        if (::outputMessageRouter.isInitialized) {
            outputMessageRouter.close()
        }
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
        // partitionId = generatePartitionId(4)
    }
}
