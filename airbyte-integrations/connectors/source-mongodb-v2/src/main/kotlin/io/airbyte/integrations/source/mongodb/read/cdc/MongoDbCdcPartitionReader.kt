/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import com.mongodb.MongoChangeStreamException
import com.mongodb.MongoCommandException
import com.mongodb.client.ChangeStreamIterable
import com.mongodb.client.model.Aggregates
import com.mongodb.client.model.Filters
import com.mongodb.client.model.changestream.ChangeStreamDocument
import com.mongodb.client.model.changestream.FullDocument
import com.mongodb.client.model.changestream.FullDocumentBeforeChange
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
import io.airbyte.integrations.source.mongodb.config.InvalidCdcCursorPositionBehavior
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfiguration
import io.airbyte.integrations.source.mongodb.discover.schemaFieldTypesOf
import io.airbyte.integrations.source.mongodb.read.partition.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodb.read.partition.RecordAcceptor
import io.airbyte.integrations.source.mongodb.read.record.MongoDbRecordConverter
import io.airbyte.integrations.source.mongodb.read.record.MongoDbSharedState
import io.airbyte.integrations.source.mongodb.read.record.MongoStringValueCodec
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.bson.BsonDocument
import org.bson.BsonTimestamp
import org.bson.Document
import org.bson.codecs.DecoderContext
import org.bson.codecs.DocumentCodec
import org.bson.conversions.Bson

private val log = KotlinLogging.logger {}

/**
 * Reads the change stream for the `Global` feed. Cold start: capture the current resume token and
 * emit nothing (the `Global` feed runs before the snapshots, so the next sync replays changes made
 * during them). Warm start: emit the changes made up to the stream's position when the read started
 * and checkpoint the token of the last emitted event.
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
     * Cold start ([resumeAfter] null): capture the current position, emit nothing. Warm start: emit
     * events until the stream is drained or an event past the position the stream had when this
     * read started was emitted, so a busy cluster cannot keep the READ open (changes made during
     * the sync are picked up by the next one). The saved position's oplog time becomes the snapshot
     * rows' cursor.
     */
    private suspend fun drain(resumeAfter: BsonDocument?) {
        if (resumeAfter == null) {
            resumeToken = currentPosition()
        } else {
            val target: BsonTimestamp = MongoDbResumeTokens.timestamp(currentPosition())
            val changeStream: ChangeStreamIterable<Document> =
                openChangeStream().resumeAfter(resumeAfter)
            changeStream.cursor().use { cursor ->
                while (true) {
                    currentCoroutineContext().ensureActive()
                    val event: ChangeStreamDocument<Document>? = cursor.tryNext()
                    if (event == null) {
                        // Drained: the post-batch token is at or past the last event.
                        resumeToken = cursor.resumeToken
                        break
                    }
                    if (emit(event)) numRecords++
                    resumeToken = event.resumeToken
                    val clusterTime: BsonTimestamp? = event.clusterTime
                    if (clusterTime != null && clusterTime > target) break
                }
            }
        }
        sharedState.snapshotCursorTime = MongoDbResumeTokens.timestamp(checkNotNull(resumeToken))
        log.info {
            if (resumeAfter == null) "CDC cold start; captured resume token."
            else "CDC read drained $numRecords change(s) up to the target."
        }
    }

    private fun openChangeStream(): ChangeStreamIterable<Document> {
        val changeStream: ChangeStreamIterable<Document> =
            watch()
                .fullDocument(FullDocument.UPDATE_LOOKUP)
                .batchSize(Int.MAX_VALUE)
                .comment(STREAM_COMMENT)
        if (sharedState.supportsPreImages) {
            // Legacy `change_streams_update_full_with_pre_image`: deletes carry the pre-image.
            changeStream.fullDocumentBeforeChange(FullDocumentBeforeChange.WHEN_AVAILABLE)
        }
        return changeStream
    }

    /**
     * The stream's current position: the post-batch resume token of one poll on a fresh cursor
     * (MongoDB 4.0.7+; earlier servers return none after an empty batch).
     */
    private fun currentPosition(): BsonDocument =
        openChangeStream().cursor().use { cursor ->
            cursor.tryNext()
            cursor.resumeToken
                ?: throw ConfigErrorException(
                    "The server returned no resume token for an empty change-stream batch; " +
                        "MongoDB 4.0.7 or later is required."
                )
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

    /**
     * Emits [event] as a record; false for an unselected collection or non-data change. A delete is
     * emitted with the document's pre-image when the collection stores one, else with its `_id`
     * only. An update or replace whose `fullDocument` is null (the document was deleted before the
     * lookup) is emitted as a delete, as the legacy connector did.
     */
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
        fun deleted(): NativeRecordPayload =
            converter.changePayload(
                event.fullDocumentBeforeChange ?: toDocument(event.documentKey),
                deletedAt = changedAt,
            )
        val payload: NativeRecordPayload =
            when (event.operationType) {
                OperationType.INSERT ->
                    converter.changePayload(event.fullDocument ?: return false, deletedAt = null)
                OperationType.UPDATE,
                OperationType.REPLACE ->
                    event.fullDocument?.let { converter.changePayload(it, deletedAt = null) }
                        ?: deleted()
                OperationType.DELETE -> deleted()
                else -> return false
            }
        payload[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(Jsons.textNode(changedAt), MongoStringValueCodec)
        stampCursor(payload, event.clusterTime)
        accept(payload, null)
        return true
    }

    /**
     * A single configured database is watched by itself, which the `read` role on that database
     * allows; several need a cluster-wide stream (`readAnyDatabase`).
     */
    private fun watch(): ChangeStreamIterable<Document> =
        configuration.databases.singleOrNull()?.let {
            sharedState.client.getDatabase(it).watch(pipeline())
        }
            ?: sharedState.client.watch(pipeline())

    /**
     * Restrict the change stream, server-side, to the configured streams' collections and to
     * data-changing operations: events of unselected collections never leave the server.
     */
    private fun pipeline(): List<Bson> =
        listOf(
            Aggregates.match(
                Filters.and(
                    Filters.or(
                        feedBootstrap.feed.streams.map {
                            Filters.and(
                                Filters.eq("ns.db", it.id.namespace),
                                Filters.eq("ns.coll", it.id.name),
                            )
                        },
                    ),
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
            checkpointPartitionId,
        )

    companion object {
        /** Tags the change-stream cursor in `currentOp` / profiler output for operators. */
        const val STREAM_COMMENT = "airbyte-source-mongodb"
        /** HistoryLost, FatalError, InvalidResumeToken, FailedToParse, empty, bad KeyString. */
        val INVALID_RESUME_TOKEN_ERROR_CODES: Set<Int> = setOf(286, 280, 260, 9, 40649, 50811)
    }
}
