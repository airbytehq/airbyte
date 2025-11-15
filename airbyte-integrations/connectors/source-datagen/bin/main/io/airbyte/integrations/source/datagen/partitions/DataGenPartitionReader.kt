/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.datagen.partitions

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.generatePartitionId
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class DataGenPartitionReader(val partition: DataGenSourcePartition) : PartitionReader {
    private val log = KotlinLogging.logger {}
    lateinit var outputMessageRouter: OutputMessageRouter

    val numRecords = AtomicLong()
    val runComplete = AtomicBoolean(false)
    protected var partitionId: String = generatePartitionId(4)
    val streamState: DataGenStreamState = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: DataGenSharedState = streamState.sharedState

    interface AcquiredResource : AutoCloseable {
        val resource: Resource.Acquired?
    }
    private val acquiredResources = AtomicReference<Map<ResourceType, AcquiredResource>>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceType =
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                DataChannelMedium.STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
                DataChannelMedium.SOCKET ->
                    listOf(ResourceType.RESOURCE_DB_CONNECTION, ResourceType.RESOURCE_OUTPUT_SOCKET)
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
        log.info { "Starting data generation for partition $partitionId in stream ${stream.name}" }

        val outputRoute = outputMessageRouter.recordAcceptors[stream.id]!!

        val configuration = sharedState.configuration
        val sourceDataGenerator = configuration.flavor.dataGenerator
        val baseCount = configuration.maxRecords / partition.modulo
        val remainder = configuration.maxRecords % partition.modulo

        val recordCountPerPartition = baseCount + if (partition.offset < remainder) 1 else 0

        for (i in 0L until recordCountPerPartition) {
            val record = sourceDataGenerator.generateData(i, partition.modulo, partition.offset)
            outputRoute(record, null)
            numRecords.incrementAndGet()
        }

        log.info {
            "Completed data generation for partition $partitionId. Total records generated: ${numRecords.get()}."
        }
        runComplete.set(true)

        return
    }

    // Only checkpoints to indicate completion. Restore from state not currently supported.
    override fun checkpoint(): PartitionReadCheckpoint {
        val opaqueStateValue =
            if (runComplete.get()) {
                DataGenStreamState.completeState
            } else {
                JsonNodeFactory.instance.objectNode()
            }
        return PartitionReadCheckpoint(
            opaqueStateValue,
            numRecords.get(),
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                DataChannelMedium.SOCKET -> partitionId
                DataChannelMedium.STDIO -> null
            }
        )
    }

    override fun releaseResources() {
        if (::outputMessageRouter.isInitialized) {
            outputMessageRouter.close()
        }
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
        partitionId = generatePartitionId(4)
    }
}
