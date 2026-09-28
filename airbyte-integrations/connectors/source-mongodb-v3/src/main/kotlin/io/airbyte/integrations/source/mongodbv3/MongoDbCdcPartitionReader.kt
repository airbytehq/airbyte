/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.databind.JsonNode
import com.mongodb.client.ChangeStreamIterable
import com.mongodb.client.MongoChangeStreamCursor
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Filters
import com.mongodb.client.model.changestream.ChangeStreamDocument
import com.mongodb.client.model.changestream.FullDocument
import com.mongodb.client.model.changestream.OperationType
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.cdk.read.UnlimitedTimePartitionReader
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
    private val converter = MongoDbRecordConverter(configuration.schemaEnforced)
    private val documentCodec = DocumentCodec()

    private val numRecords = AtomicLong(0L)
    private val newResumeToken = AtomicReference<BsonDocument?>(null)

    private val acquiredResources = AtomicReference<Map<ResourceType, ReaderAcquiredResource>>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resources: Map<ResourceType, ReaderAcquiredResource> =
            sharedState.tryAcquireResourcesForReader(listOf(ResourceType.RESOURCE_DB_CONNECTION))
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
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
            val consumers: Map<StreamIdentifier, StreamRecordConsumer> =
                feedBootstrap.streamRecordConsumers()
            while (true) {
                currentCoroutineContext().ensureActive()
                val event: ChangeStreamDocument<Document> = cursor.tryNext() ?: break
                emit(event, consumers)
                newResumeToken.set(event.resumeToken)
            }
            newResumeToken.compareAndSet(null, cursor.resumeToken)
            log.info { "CDC read drained ${numRecords.get()} change(s)." }
        }
    }

    private fun emit(
        event: ChangeStreamDocument<Document>,
        consumers: Map<StreamIdentifier, StreamRecordConsumer>,
    ) {
        val namespace = event.namespace ?: return
        val streamID: StreamIdentifier =
            StreamIdentifier.from(
                StreamDescriptor()
                    .withName(namespace.collectionName)
                    .withNamespace(namespace.databaseName),
            )
        val consumer: StreamRecordConsumer = consumers[streamID] ?: return
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
            FieldValueEncoder(textNode(updatedAt), MongoDbJsonNodeEncoder)
        consumer.accept(payload, null)
        numRecords.incrementAndGet()
    }

    private fun clusterTime(event: ChangeStreamDocument<Document>): String =
        event.clusterTime?.let { Instant.ofEpochSecond(it.time.toLong()).toString() }
            ?: Instant.now().toString()

    private fun toDocument(bson: BsonDocument?): Document =
        bson?.let { documentCodec.decode(it.asBsonReader(), DecoderContext.builder().build()) }
            ?: Document()

    private fun textNode(value: String): JsonNode = io.airbyte.cdk.util.Jsons.textNode(value)

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
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
    }

    /** The streams (collections) covered by the change stream: those in the [Global] feed. */
    val globalStreams: Global
        get() = feedBootstrap.feed
}
