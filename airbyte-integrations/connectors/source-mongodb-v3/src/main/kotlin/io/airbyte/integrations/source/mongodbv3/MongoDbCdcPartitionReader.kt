/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.ChangeStreamIterable
import com.mongodb.client.MongoChangeStreamCursor
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Filters
import com.mongodb.client.model.changestream.ChangeStreamDocument
import com.mongodb.client.model.changestream.FullDocument
import com.mongodb.client.model.changestream.OperationType
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.UnlimitedTimePartitionReader
import io.airbyte.cdk.read.generatePartitionId
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.bson.BsonDocument
import org.bson.Document
import org.bson.codecs.DecoderContext
import org.bson.codecs.DocumentCodec
import org.bson.conversions.Bson

private val log = KotlinLogging.logger {}

/**
 * Reads the MongoDB replica-set change stream for the `Global` feed with the native driver
 * `watch()` (no Debezium).
 * - **Cold start** (no prior state): opens the change stream, captures the current resume token,
 * and emits no records. Because the `Global` feed runs before the snapshot `Stream` feeds, this
 * token predates the snapshots, so the next sync replays any changes that happened during the
 * snapshot.
 * - **Warm start**: resumes from the saved token and drains all currently-available changes
 * (`tryNext()` until it returns null), emitting insert/update/replace as upserts and delete as a
 * record with `_ab_cdc_deleted_at` set, then checkpoints the new resume token.
 */
class MongoDbCdcPartitionReader(
    private val sharedState: MongoDbSharedState,
    private val feedBootstrap: GlobalFeedBootstrap,
) : UnlimitedTimePartitionReader {

    private val configuration: MongoDbSourceConfiguration = sharedState.configuration
    private val documentCodec = DocumentCodec()
    /** One converter per stream, each carrying that stream's schema for typed protobuf encoding. */
    private val convertersByStream: Map<StreamIdentifier, MongoDbRecordConverter> =
        feedBootstrap.feed.streams.associate { stream: Stream ->
            stream.id to
                MongoDbRecordConverter(configuration.schemaEnforced, schemaFieldTypesOf(stream))
        }

    private val numRecords = AtomicLong(0L)
    private val newResumeToken = AtomicReference<BsonDocument?>(null)
    private var partitionId: String = generatePartitionId(4)
    private lateinit var outputMessageRouter: OutputMessageRouter

    private val acquiredResources = AtomicReference<Map<ResourceType, ReaderAcquiredResource>>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceTypes: List<ResourceType> =
            when (feedBootstrap.dataChannelMedium) {
                DataChannelMedium.STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
                DataChannelMedium.SOCKET ->
                    listOf(ResourceType.RESOURCE_DB_CONNECTION, ResourceType.RESOURCE_OUTPUT_SOCKET)
            }
        val resources: Map<ResourceType, ReaderAcquiredResource> =
            sharedState.tryAcquireResourcesForReader(resourceTypes)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        outputMessageRouter =
            OutputMessageRouter(
                feedBootstrap.dataChannelMedium,
                feedBootstrap.dataChannelFormat,
                feedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                feedBootstrap,
                resources.mapNotNull { (type, r) -> r.resource?.let { type to it } }.toMap(),
            )
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        val priorState: MongoDbCdcState? =
            MongoDbCdcState.fromOpaqueStateValue(feedBootstrap.currentState)
        val priorToken: BsonDocument? = priorState?.resumeTokenBson()

        val iterable: ChangeStreamIterable<Document> =
            sharedState.client.watch(pipeline()).apply {
                fullDocument(
                    when (configuration.updateCaptureMode) {
                        UpdateCaptureMode.LOOKUP -> FullDocument.UPDATE_LOOKUP
                        UpdateCaptureMode.POST_IMAGE -> FullDocument.REQUIRED
                    },
                )
                priorToken?.let { resumeAfter(it) }
            }

        iterable.cursor().use { cursor: MongoChangeStreamCursor<ChangeStreamDocument<Document>> ->
            if (priorToken == null) {
                // Cold start: capture the current position, emit nothing.
                cursor.tryNext()
                newResumeToken.set(cursor.resumeToken)
                log.info { "CDC cold start; captured resume token." }
                return
            }
            while (true) {
                currentCoroutineContext().ensureActive()
                val event: ChangeStreamDocument<Document> = cursor.tryNext() ?: break
                emit(event)
                newResumeToken.set(event.resumeToken)
            }
            newResumeToken.compareAndSet(null, cursor.resumeToken)
            log.info { "CDC read drained ${numRecords.get()} change(s)." }
        }
    }

    private fun emit(event: ChangeStreamDocument<Document>) {
        val namespace = event.namespace ?: return
        val streamID: StreamIdentifier =
            StreamIdentifier.from(
                StreamDescriptor()
                    .withName(namespace.collectionName)
                    .withNamespace(namespace.databaseName),
            )
        val outputRoute = outputMessageRouter.recordAcceptors[streamID] ?: return
        val converter: MongoDbRecordConverter = convertersByStream[streamID] ?: return
        val updatedAt: String = clusterTime(event)
        val payload: NativeRecordPayload =
            when (event.operationType) {
                OperationType.INSERT,
                OperationType.UPDATE,
                OperationType.REPLACE -> {
                    val fullDocument: Document = event.fullDocument ?: return
                    converter.changePayload(fullDocument, deletedAt = null)
                }
                OperationType.DELETE ->
                    converter.changePayload(toDocument(event.documentKey), deletedAt = updatedAt)
                else -> return
            }
        payload[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(Jsons.textNode(updatedAt), MongoStringValueCodec)
        outputRoute(payload, null)
        numRecords.incrementAndGet()
    }

    private fun clusterTime(event: ChangeStreamDocument<Document>): String =
        event.clusterTime?.let { Instant.ofEpochSecond(it.time.toLong()).toString() }
            ?: Instant.now().toString()

    private fun toDocument(bson: BsonDocument?): Document =
        bson?.let { documentCodec.decode(it.asBsonReader(), DecoderContext.builder().build()) }
            ?: Document()

    /** Restrict the change stream to the configured databases and to data-changing operations. */
    private fun pipeline(): List<Bson> =
        listOf(
            Aggregates.match(
                Filters.and(
                    Filters.`in`("ns.db", configuration.databases),
                    Filters.`in`(
                        "operationType",
                        listOf("insert", "update", "replace", "delete"),
                    ),
                ),
            ),
        )

    override fun checkpoint(): PartitionReadCheckpoint =
        PartitionReadCheckpoint(
            MongoDbCdcState.of(newResumeToken.get(), configuration.schemaEnforced)
                .toOpaqueStateValue(),
            numRecords.get(),
        )

    override fun releaseResources() {
        if (::outputMessageRouter.isInitialized) {
            outputMessageRouter.close()
        }
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
        partitionId = generatePartitionId(4)
    }

    /** The streams (collections) covered by the change stream: those in the [Global] feed. */
    val globalStreams: Global
        get() = feedBootstrap.feed
}
