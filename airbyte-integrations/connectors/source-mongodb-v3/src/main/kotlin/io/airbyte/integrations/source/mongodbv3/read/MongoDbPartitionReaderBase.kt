/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.generatePartitionId

/** A function that emits one record for a stream. */
typealias RecordAcceptor = (NativeRecordPayload, Map<EmittedField, FieldValueChange>?) -> Unit

/**
 * Shared lifecycle of the snapshot and CDC readers: acquires a DB-connection slot (plus an output
 * socket on the socket channel), builds the [OutputMessageRouter] that routes records to STDIO or
 * the socket data channel, and releases both. Subclasses implement `run()` and `checkpoint()`.
 */
abstract class MongoDbPartitionReaderBase(
    protected val sharedState: MongoDbSharedState,
    private val feedBootstrap: FeedBootstrap<*>,
) : PartitionReader {

    private val partitionId: String = generatePartitionId(4)
    private var acquiredResources: Map<ResourceType, Resource.Acquired>? = null
    private var outputMessageRouter: OutputMessageRouter? = null

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceTypes: List<ResourceType> =
            when (feedBootstrap.dataChannelMedium) {
                DataChannelMedium.STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
                DataChannelMedium.SOCKET ->
                    listOf(ResourceType.RESOURCE_DB_CONNECTION, ResourceType.RESOURCE_OUTPUT_SOCKET)
            }
        val resources: Map<ResourceType, Resource.Acquired> =
            sharedState.tryAcquireResourcesForReader(resourceTypes)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources = resources
        outputMessageRouter =
            OutputMessageRouter(
                feedBootstrap.dataChannelMedium,
                feedBootstrap.dataChannelFormat,
                feedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                feedBootstrap,
                resources,
            )
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    /** The record acceptor for [streamId], or null if the stream is not part of this feed. */
    protected fun recordAcceptorFor(streamId: StreamIdentifier): RecordAcceptor? =
        checkNotNull(outputMessageRouter) { "resources not acquired" }.recordAcceptors[streamId]

    override fun releaseResources() {
        outputMessageRouter?.close()
        outputMessageRouter = null
        acquiredResources?.values?.forEach { it.close() }
        acquiredResources = null
    }
}
