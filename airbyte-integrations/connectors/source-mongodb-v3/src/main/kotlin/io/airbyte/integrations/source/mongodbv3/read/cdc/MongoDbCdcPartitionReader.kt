/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.cdc

import com.mongodb.MongoChangeStreamException
import com.mongodb.MongoCommandException
import com.mongodb.client.ChangeStreamIterable
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Filters
import com.mongodb.client.model.changestream.ChangeStreamDocument
import com.mongodb.client.model.changestream.FullDocument
import com.mongodb.client.model.changestream.OperationType
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.UnlimitedTimePartitionReader
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodbv3.config.InvalidCdcCursorPositionBehavior
import io.airbyte.integrations.source.mongodbv3.config.MongoDbSourceConfiguration
import io.airbyte.integrations.source.mongodbv3.config.UpdateCaptureMode
import io.airbyte.integrations.source.mongodbv3.read.partition.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodbv3.read.partition.RecordAcceptor
import io.airbyte.integrations.source.mongodbv3.read.record.MongoDbRecordConverter
import io.airbyte.integrations.source.mongodbv3.read.record.MongoDbSharedState
import io.airbyte.integrations.source.mongodbv3.read.record.MongoStringValueCodec
import io.airbyte.integrations.source.mongodbv3.read.record.schemaFieldTypesOf
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
 * Reads the change stream for the `Global` feed. Cold start: capture the current resume token and
 * emit nothing (the `Global` feed runs before the snapshots, so the next sync replays changes made
 * during them). Warm start: drain the available changes and checkpoint the new token.
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
        if (priorToken == null) {
            drain(resumeAfter = null)
            return
        }
        try {
            drain(resumeAfter = priorToken)
        } catch (e: Exception) {
            if (!isInvalidResumeToken(e)) throw e
            when (configuration.invalidCdcCursorPositionBehavior) {
                InvalidCdcCursorPositionBehavior.FAIL_SYNC ->
                    throw ConfigErrorException(
                        "Saved offset is not valid. Please reset the connection, and then increase " +
                            "oplog retention and/or increase sync frequency to prevent this from " +
                            "happening in the future. See " +
                            "https://docs.airbyte.com/integrations/sources/mongodb-v2#mongodb-oplog-and-change-streams " +
                            "for more details",
                        e,
                    )
                InvalidCdcCursorPositionBehavior.RESYNC_DATA -> {
                    log.warn(e) { "Saved resume token is not valid; resetting state to re-sync." }
                    // Clears the token and every incremental snapshot state: re-snapshot from
                    // scratch.
                    feedBootstrap.resetAll()
                    drain(resumeAfter = null)
                }
            }
        }
    }

    /**
     * Cold start ([resumeAfter] null): one poll to establish the position, nothing emitted. Warm
     * start: emit every available change. The cursor's final position is the new resume token.
     */
    private suspend fun drain(resumeAfter: BsonDocument?) {
        val changeStream: ChangeStreamIterable<Document> =
            sharedState.client.watch(pipeline()).fullDocument(fullDocumentMode())
        resumeAfter?.let { changeStream.resumeAfter(it) }
        changeStream.cursor().use { cursor ->
            if (resumeAfter == null) {
                cursor.tryNext()
            } else {
                while (true) {
                    currentCoroutineContext().ensureActive()
                    if (emit(cursor.tryNext() ?: break)) numRecords++
                }
            }
            resumeToken = cursor.resumeToken
        }
        log.info {
            if (resumeAfter == null) "CDC cold start; captured resume token."
            else "CDC read drained $numRecords change(s)."
        }
    }

    /**
     * Whether the saved token can no longer be resumed from (oplog rolled past it, or the server
     * rejected it). The server *accepts* any well-formed token, even for a nonsensical cluster
     * time, so only a rejected token is detectable.
     */
    private fun isInvalidResumeToken(e: Throwable): Boolean =
        generateSequence(e) { it.cause }
            .any {
                it is MongoChangeStreamException ||
                    (it is MongoCommandException &&
                        it.errorCode in INVALID_RESUME_TOKEN_ERROR_CODES)
            }

    /** Emits [event] as a record; false for an unselected collection or non-data change. */
    private fun emit(event: ChangeStreamDocument<Document>): Boolean {
        val namespace = event.namespace ?: return false
        val streamId =
            StreamIdentifier.from(
                StreamDescriptor()
                    .withName(namespace.collectionName)
                    .withNamespace(namespace.databaseName),
            )
        val accept: RecordAcceptor = recordAcceptorFor(streamId) ?: return false
        val converter: MongoDbRecordConverter = convertersByStream[streamId] ?: return false
        val changedAt: String = clusterTime(event)
        val payload: NativeRecordPayload =
            when (event.operationType) {
                OperationType.INSERT,
                OperationType.UPDATE,
                OperationType.REPLACE ->
                    converter.changePayload(event.fullDocument ?: return false, deletedAt = null)
                OperationType.DELETE ->
                    converter.changePayload(toDocument(event.documentKey), deletedAt = changedAt)
                else -> return false
            }
        payload[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(Jsons.textNode(changedAt), MongoStringValueCodec)
        accept(payload, null)
        return true
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

    companion object {
        /** HistoryLost, FatalError, InvalidResumeToken, FailedToParse, empty, bad KeyString. */
        val INVALID_RESUME_TOKEN_ERROR_CODES: Set<Int> = setOf(286, 280, 260, 9, 40649, 50811)
    }
}
