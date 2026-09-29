/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.ChangeStreamIterable
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Filters
import com.mongodb.client.model.changestream.ChangeStreamDocument
import com.mongodb.client.model.changestream.FullDocument
import com.mongodb.client.model.changestream.OperationType
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.UnlimitedTimePartitionReader
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
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
    sharedState: MongoDbSharedState,
    private val feedBootstrap: GlobalFeedBootstrap,
) : MongoDbPartitionReaderBase(sharedState, feedBootstrap), UnlimitedTimePartitionReader {

    private val configuration: MongoDbSourceConfiguration = sharedState.configuration
    private val documentCodec = DocumentCodec()
    /** One converter per stream, each carrying that stream's schema for typed protobuf encoding. */
    private val convertersByStream: Map<StreamIdentifier, MongoDbRecordConverter> =
        feedBootstrap.feed.streams.associate {
            it.id to MongoDbRecordConverter(configuration.schemaEnforced, schemaFieldTypesOf(it))
        }

    @Volatile private var numRecords = 0L
    @Volatile private var resumeToken: BsonDocument? = null

    override suspend fun run() {
        val priorToken: BsonDocument? =
            MongoDbCdcState.fromOpaqueStateValue(feedBootstrap.currentState)?.resumeTokenBson()
        val changeStream: ChangeStreamIterable<Document> =
            sharedState.client.watch(pipeline()).fullDocument(fullDocumentMode())
        priorToken?.let { changeStream.resumeAfter(it) }

        changeStream.cursor().use { cursor ->
            if (priorToken == null) {
                // Cold start: one poll establishes the position; emit nothing.
                cursor.tryNext()
            } else {
                while (true) {
                    currentCoroutineContext().ensureActive()
                    emit(cursor.tryNext() ?: break)
                }
            }
            resumeToken = cursor.resumeToken
        }
        log.info {
            if (priorToken == null) "CDC cold start; captured resume token."
            else "CDC read drained $numRecords change(s)."
        }
    }

    private fun emit(event: ChangeStreamDocument<Document>) {
        val namespace = event.namespace ?: return
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor()
                    .withName(namespace.collectionName)
                    .withNamespace(namespace.databaseName),
            )
        val accept: RecordAcceptor = recordAcceptorFor(streamId) ?: return
        val converter: MongoDbRecordConverter = convertersByStream[streamId] ?: return
        val changedAt: String = clusterTime(event)
        val payload: NativeRecordPayload =
            when (event.operationType) {
                OperationType.INSERT,
                OperationType.UPDATE,
                OperationType.REPLACE ->
                    converter.changePayload(event.fullDocument ?: return, deletedAt = null)
                OperationType.DELETE ->
                    converter.changePayload(toDocument(event.documentKey), deletedAt = changedAt)
                else -> return
            }
        payload[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(Jsons.textNode(changedAt), MongoStringValueCodec)
        accept(payload, null)
        numRecords++
    }

    private fun fullDocumentMode(): FullDocument =
        when (configuration.updateCaptureMode) {
            UpdateCaptureMode.LOOKUP -> FullDocument.UPDATE_LOOKUP
            UpdateCaptureMode.POST_IMAGE -> FullDocument.REQUIRED
        }

    /** Restrict the change stream to the configured databases and to data-changing operations. */
    private fun pipeline(): List<Bson> =
        listOf(
            Aggregates.match(
                Filters.and(
                    Filters.`in`("ns.db", configuration.databases),
                    Filters.`in`("operationType", listOf("insert", "update", "replace", "delete")),
                ),
            ),
        )

    private fun clusterTime(event: ChangeStreamDocument<Document>): String =
        (event.clusterTime?.let { Instant.ofEpochSecond(it.time.toLong()) } ?: Instant.now())
            .toString()

    private fun toDocument(bson: BsonDocument?): Document =
        bson?.let { documentCodec.decode(it.asBsonReader(), DecoderContext.builder().build()) }
            ?: Document()

    override fun checkpoint(): PartitionReadCheckpoint =
        PartitionReadCheckpoint(
            MongoDbCdcState.of(resumeToken, configuration.schemaEnforced).toOpaqueStateValue(),
            numRecords,
        )
}
