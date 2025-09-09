package io.airbyte.integrations.source.datagen.partitionops

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.output.DataChannelMedium.*
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.ResourceType.RESOURCE_DB_CONNECTION
import io.airbyte.cdk.read.ResourceType.RESOURCE_OUTPUT_SOCKET
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSharedState
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenSourcePartition
import io.airbyte.integrations.source.datagen.partitionobjs.DataGenStreamState
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class DataGenPartitionReader (val partition: DataGenSourcePartition) : PartitionReader {
    lateinit var outputMessageRouter: OutputMessageRouter
    val numRecords = AtomicLong()
    val runComplete = AtomicBoolean(false)
    // dont need this rn cuz just doing 1 partition
    // protected var partitionId: String = generatePartitionId(4)
    protected var partitionId: String = "0"
    val streamState: DataGenStreamState = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: DataGenSharedState = streamState.sharedState

    interface AcquiredResource : AutoCloseable {
        val resource: Resource.Acquired?
    }
    private val acquiredResources = AtomicReference<Map<ResourceType,AcquiredResource>>()

    override fun tryAcquireResources() : PartitionReader.TryAcquireResourcesStatus{
        val resourceType =
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                STDIO -> listOf(RESOURCE_DB_CONNECTION)
                SOCKET ->
                    listOf(RESOURCE_DB_CONNECTION, RESOURCE_OUTPUT_SOCKET)
            }

        val resources: Map<ResourceType, AcquiredResource> =
            sharedState.tryAcquireResourcesForReader(resourceType)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER

        acquiredResources.set(resources)
        outputMessageRouter =
            OutputMessageRouter(
                streamState.streamFeedBootstrap.dataChannelMedium,
                streamState.streamFeedBootstrap.dataChannelFormat,
                streamState.streamFeedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                streamState.streamFeedBootstrap,
                acquiredResources
                    .get()
                    .filter { it.value.resource != null }
                    .map { it.key to it.value.resource!! }
                    .toMap()
            )
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        val outputRoute = outputMessageRouter.recordAcceptors[stream.id]!!

        val configuration = sharedState.configuration
        val sourceDataGenerator = configuration.flavor.dataGenerator
        val record = sourceDataGenerator.generateData()
        outputRoute(record, null)
        numRecords.incrementAndGet()

        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
//        return PartitionReadCheckpoint(
//            streamFeedBootstrap.currentState ?: Jsons.objectNode(),
//            (acquiredResources.get().size).toLong(),
//            when (streamFeedBootstrap.dataChannelMedium) {
//                STDIO -> null
//                SOCKET -> partitionId
//            }
//        )
        return PartitionReadCheckpoint(
            com.fasterxml.jackson.databind.node.JsonNodeFactory.instance.objectNode(),
            numRecords.get(),
            null
        )
    }

    override fun releaseResources() {
        if (::outputMessageRouter.isInitialized) {
            outputMessageRouter.close()
        }
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
        // partitionId = generatePartitionId(4)
    }
}
