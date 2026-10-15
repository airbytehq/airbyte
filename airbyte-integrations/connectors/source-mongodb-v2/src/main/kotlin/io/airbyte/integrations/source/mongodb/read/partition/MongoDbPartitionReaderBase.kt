/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.partition

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.data.LongCodec
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
import io.airbyte.integrations.source.mongodb.discover.MongoDbMetaFieldDecorator
import io.airbyte.integrations.source.mongodb.read.record.MongoDbSharedState
import java.time.OffsetDateTime
import java.time.ZoneOffset

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

    private val metaFieldDecorator: MongoDbMetaFieldDecorator =
        feedBootstrap.metaFieldDecorator as MongoDbMetaFieldDecorator
    private val emittedAt: OffsetDateTime =
        feedBootstrap.outputConsumer.recordEmittedAt.atOffset(ZoneOffset.UTC)

    /**
     * Stamps [payload] with the next `_ab_cdc_cursor` of the sync-wide sequence. Only change events
     * carry a cursor (snapshot rows keep the decorator's null): dedup destinations rank nulls last,
     * so a change always supersedes the snapshot row, and the CDK never decorates the `Global`
     * feed's records, hence the reader does it per event.
     */
    protected fun stampCursor(payload: NativeRecordPayload) {
        payload[MongoDbMetaField.CDC_CURSOR.id] =
            FieldValueEncoder(metaFieldDecorator.nextCursor(emittedAt), LongCodec)
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

    override fun releaseResources() {
        outputMessageRouter?.close()
        outputMessageRouter = null
        acquiredResources?.values?.forEach { it.close() }
        acquiredResources = null
    }
}
