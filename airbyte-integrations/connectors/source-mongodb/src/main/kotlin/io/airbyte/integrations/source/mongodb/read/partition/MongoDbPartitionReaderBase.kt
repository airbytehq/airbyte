/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.partition

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.generatePartitionId
import io.airbyte.integrations.source.mongodb.discover.MongoDbMetaField
import io.airbyte.integrations.source.mongodb.read.record.MongoDbSharedState
import org.bson.BsonTimestamp

/** A function that emits one record for a stream. */
typealias RecordAcceptor = (NativeRecordPayload, Map<EmittedField, FieldValueChange>?) -> Unit

/**
 * Shared reader lifecycle: acquire a DB-connection slot (and an output socket on the socket
 * channel), build the [OutputMessageRouter], release both. Subclasses implement `run()` and
 * `checkpoint()`.
 */
abstract class MongoDbPartitionReaderBase(
    protected val sharedState: MongoDbSharedState,
    private val feedBootstrap: FeedBootstrap<*>,
) : PartitionReader {

    private val partitionId: String = generatePartitionId(4)
    private var acquiredResources: Map<ResourceType, Resource.Acquired>? = null
    private var outputMessageRouter: OutputMessageRouter? = null

    /**
     * The partition id to put in the checkpoint: on the socket channel, state messages carry it so
     * the destination can tie the records of a socket to their state; absent on STDIO.
     */
    protected val checkpointPartitionId: String?
        get() =
            when (feedBootstrap.dataChannelMedium) {
                DataChannelMedium.SOCKET -> partitionId
                DataChannelMedium.STDIO -> null
            }

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

    /**
     * Stamps [payload] with `_ab_cdc_cursor`: a MongoDB cluster time as a long — the time the READ
     * started for a snapshot row, the event's own time for a change — so a change sorts above the
     * row it supersedes exactly when it happened after the snapshot began, and the same event
     * always gets the same cursor. The CDK's decorator only fills the default record with null.
     */
    protected fun stampCursor(payload: NativeRecordPayload, clusterTime: BsonTimestamp?) {
        payload[MongoDbMetaField.CDC_CURSOR.id] =
            if (clusterTime == null) FieldValueEncoder(null, NullCodec)
            else FieldValueEncoder(clusterTime.value, LongCodec)
    }

    override fun releaseResources() {
        outputMessageRouter?.close()
        outputMessageRouter = null
        acquiredResources?.values?.forEach { it.close() }
        acquiredResources = null
    }
}
