/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.cdc

import com.mongodb.MongoChangeStreamException
import com.mongodb.MongoCommandException
import com.mongodb.MongoNamespace
import com.mongodb.client.ChangeStreamIterable
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
import io.airbyte.integrations.source.mongodb.config.InvalidCdcCursorPositionBehavior
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfiguration
import io.airbyte.integrations.source.mongodb.discover.schemaFieldTypesOf
import io.airbyte.integrations.source.mongodb.read.partition.MongoDbPartitionReaderBase
import io.airbyte.integrations.source.mongodb.read.partition.RecordAcceptor
import io.airbyte.integrations.source.mongodb.read.record.MongoDbRecordConverter
import io.airbyte.integrations.source.mongodb.read.record.MongoDbSharedState
import io.airbyte.integrations.source.mongodb.read.record.MongoDbValue
import io.airbyte.integrations.source.mongodb.read.record.MongoStringValueCodec
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbStreamStateValue
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.bson.BsonDocument
import org.bson.BsonTimestamp
import org.bson.RawBsonDocument
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

    private class Target(val accept: RecordAcceptor, val converter: MongoDbRecordConverter)

    /**
     * Where each collection's events go, keyed as the events name it; one lookup per event. Built
     * on first use, once the output router exists.
     */
    private val targets: Map<MongoNamespace, Target> by lazy {
        feedBootstrap.feed.streams
            .mapNotNull { stream ->
                val accept: RecordAcceptor = recordAcceptorFor(stream.id) ?: return@mapNotNull null
                val converter =
                    MongoDbRecordConverter(configuration.schemaEnforced, schemaFieldTypesOf(stream))
                MongoNamespace(stream.id.namespace!!, stream.id.name) to Target(accept, converter)
            }
            .toMap()
    }

    @Volatile private var numRecords = 0L
    private var inserts = 0L
    private var updates = 0L
    private var deletes = 0L
    private var discarded = 0L
    private val changesByNamespace = LinkedHashMap<MongoNamespace, Long>()
    @Volatile private var resumeToken: BsonDocument? = null
    /** Oplog time (seconds) of [resumeToken]; see [MongoDbCdcState.cdcSyncedUntil]. */
    @Volatile private var cdcSyncedUntil: Instant? = null
    /** The state the read started from; its legacy variables are carried into the checkpoint. */
    @Volatile private var priorState: MongoDbCdcState? = null

    override suspend fun run() {
        priorState = MongoDbCdcState.fromOpaqueStateValue(feedBootstrap.currentState)
        val priorToken: BsonDocument? = priorState?.resumeTokenBson()
        sharedState.logOplog(priorToken)
        try {
            drain(resumeAfter = priorToken)
        } catch (e: Exception) {
            if (priorToken == null || !isInvalidResumeToken(e)) throw e
            when (configuration.invalidCdcCursorPositionBehavior) {
                InvalidCdcCursorPositionBehavior.FAIL_SYNC ->
                    throw ConfigErrorException(
                        if (isHistoryLost(e)) {
                            "Saved offset is not valid. Please refresh or clear the connection, and then " +
                                "increase oplog retention and/or increase sync frequency to " +
                                "prevent this from happening in the future. See " +
                                "https://docs.airbyte.com/integrations/sources/mongodb/mongodb-troubleshooting#mongodb-oplog-and-change-streams " +
                                "for more details"
                        } else {
                            "The saved change stream position cannot be read by the server " +
                                "(${e.message}). The connection's state is corrupt or was taken " +
                                "from another cluster; please refresh or clear the connection."
                        },
                        e,
                    )
                InvalidCdcCursorPositionBehavior.RESYNC_DATA -> {
                    log.warn(e) { "Saved resume token is not valid; resetting state to re-sync." }
                    // Clears the token and every incremental snapshot state: re-snapshot from
                    // scratch.
                    feedBootstrap.resetAll()
                    priorState = null // a reset carries nothing, the legacy variables included
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
        logWatchedStreams(coldStart = resumeAfter == null)
        if (resumeAfter == null) {
            resumeToken = currentPosition()
        } else {
            val target: BsonTimestamp = clusterTimeNow()
            val changeStream: ChangeStreamIterable<RawBsonDocument> =
                openChangeStream().resumeAfter(resumeAfter)
            changeStream.cursor().use { cursor ->
                var emptyPolls = 0
                while (true) {
                    currentCoroutineContext().ensureActive()
                    val event: ChangeStreamDocument<RawBsonDocument>? = cursor.tryNext()
                    if (event == null) {
                        // An empty batch is "drained" only once the post-batch token has reached
                        // the target. Through `mongos` the token is the minimum over the shards
                        // and an event is held back until every shard has passed it, so an empty
                        // batch can precede events that are already committed; poll on until the
                        // idle shard's periodic no-op moves it, within a bound.
                        resumeToken = cursor.resumeToken
                        val position: BsonTimestamp? = resumeToken?.let {
                            MongoDbResumeTokens.timestamp(it)
                        }
                        if (position == null || position >= target) break
                        if (++emptyPolls >= MAX_EMPTY_POLLS) {
                            log.warn {
                                "The change stream position ($position) did not reach the " +
                                    "target ($target) after $emptyPolls empty polls; stopping " +
                                    "here, the rest is read by the next sync."
                            }
                            break
                        }
                        continue
                    }
                    emptyPolls = 0
                    if (emit(event)) {
                        numRecords++
                        event.namespace?.let { changesByNamespace.merge(it, 1L, Long::plus) }
                    } else discarded += 1L
                    resumeToken = event.resumeToken
                    val clusterTime: BsonTimestamp? = event.clusterTime
                    if (clusterTime != null && clusterTime > target) break
                }
            }
        }
        cdcSyncedUntil =
            Instant.ofEpochSecond(
                MongoDbResumeTokens.timestamp(checkNotNull(resumeToken)).time.toLong(),
            )
        log.info {
            if (resumeAfter == null) "CDC cold start; captured resume token."
            else
                "CDC read drained $numRecords change(s) up to the target: $inserts insert(s), " +
                    "$updates update(s), $deletes delete(s); $discarded event(s) discarded" +
                    (if (changesByNamespace.isEmpty()) "."
                    else
                        "; per stream: " +
                            changesByNamespace.entries.joinToString(", ") { (ns, n) ->
                                "${ns.fullName} $n"
                            } +
                            ".")
        }
    }

    private fun openChangeStream(): ChangeStreamIterable<RawBsonDocument> {
        val changeStream: ChangeStreamIterable<RawBsonDocument> =
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
     * Where a warm drain stops: the cluster time the server gossips, which is at or past every
     * write committed before the call on every shard. A fresh cursor's post-batch token would not
     * do here: through `mongos` it is the minimum over the shards, and an idle shard's position
     * only moves with its periodic no-op, so the drain would stop short of recent writes. (The
     * snapshot cursor is a different matter: it comes from the checkpointed token.)
     */
    private fun clusterTimeNow(): BsonTimestamp =
        sharedState.client
            .getDatabase("admin")
            .runCommand(BsonDocument("hello", org.bson.BsonInt32(1)), BsonDocument::class.java)
            .getDocument("\$clusterTime")
            .getTimestamp("clusterTime")
            .value
            .let { BsonTimestamp(it) }

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
                        "MongoDB 4.0.7 or later is required.",
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

    /** ChangeStreamHistoryLost: the position is well-formed but the oplog no longer holds it. */
    private fun isHistoryLost(e: Throwable): Boolean =
        generateSequence(e) { it.cause }
            .any { it is MongoCommandException && it.errorCode == CHANGE_STREAM_HISTORY_LOST }

    /**
     * Emits [event] as a record; false for an unselected collection or non-data change. A delete is
     * emitted with the document's pre-image when the collection stores one, else with its `_id`
     * only. An update or replace whose `fullDocument` is null (the document was deleted before the
     * lookup) is emitted as a delete, as the legacy connector did.
     */
    private fun emit(event: ChangeStreamDocument<RawBsonDocument>): Boolean {
        val target: Target = targets[event.namespace ?: return false] ?: return false
        val converter: MongoDbRecordConverter = target.converter
        val changedAt: String = clusterTime(event)
        fun deleted(): NativeRecordPayload =
            converter
                .changePayload(
                    event.fullDocumentBeforeChange ?: event.documentKey ?: BsonDocument(),
                    deletedAt = changedAt,
                )
                .also { deletes++ }
        val payload: NativeRecordPayload =
            when (event.operationType) {
                null -> return false
                OperationType.INSERT ->
                    converter
                        .changePayload(event.fullDocument ?: return false, deletedAt = null)
                        .also {
                            inserts++
                        }
                OperationType.UPDATE,
                OperationType.REPLACE ->
                    event.fullDocument?.let {
                        converter.changePayload(it, deletedAt = null).also { updates++ }
                    } ?: deleted()
                OperationType.DELETE -> deleted()
                else -> return false
            }
        payload[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(MongoDbValue.Text(changedAt), MongoStringValueCodec)
        stampCursor(payload, event.clusterTime)
        target.accept(payload, null)
        return true
    }

    /**
     * The streams whose changes this read replays: those with a checkpoint (snapshot started or
     * complete), as the legacy connector's Debezium include list. A stream snapshotted for the
     * first time in this sync is not watched: its documents written after the saved token are in
     * that snapshot, and the next sync replays what follows. Empty on a cold start, which only
     * captures the position.
     */
    private fun watchedStreams(): List<StreamIdentifier> =
        feedBootstrap.feed.streams
            .filter {
                // The CDK writes `{}` for a stream that has not checkpointed yet: not a checkpoint.
                MongoDbStreamStateValue.fromCurrentState(feedBootstrap.currentState(it)) != null
            }
            .map { it.id }

    /** Which streams this read replays changes for, and which wait for their first checkpoint. */
    private fun logWatchedStreams(coldStart: Boolean) {
        val watched: List<StreamIdentifier> = watchedStreams()
        val deferred: List<StreamIdentifier> =
            feedBootstrap.feed.streams.map { it.id }.filterNot { it in watched }
        log.info {
            (if (coldStart) "CDC cold start: " else "CDC read: ") +
                "${watched.size} stream(s) watched" +
                (if (watched.isEmpty()) "" else " (${namespaces(watched)})") +
                (if (deferred.isEmpty()) "."
                else
                    "; ${deferred.size} snapshotting this sync, watched from the next " +
                        "(${namespaces(deferred)}).")
        }
    }

    /** `db.coll, db.other` — the first [NAMESPACES_LOGGED], then "and N more". */
    private fun namespaces(streams: Collection<StreamIdentifier>): String {
        val names: List<String> = streams.map { "${it.namespace}.${it.name}" }
        val shown: String = names.take(NAMESPACES_LOGGED).joinToString(", ")
        val more: Int = names.size - NAMESPACES_LOGGED
        return if (more > 0) "$shown and $more more" else shown
    }

    /**
     * A single configured database is watched by itself, which the `read` role on that database
     * allows; several need a cluster-wide stream (`readAnyDatabase`).
     */
    private fun watch(): ChangeStreamIterable<RawBsonDocument> {
        val pipeline: List<Bson> =
            MongoDbChangeStreamPipeline.build(
                watchedStreams(),
                preImages = sharedState.supportsPreImages,
            )
        return configuration.databases.singleOrNull()?.let {
            sharedState.client.getDatabase(it).watch(pipeline, RawBsonDocument::class.java)
        } ?: sharedState.client.watch(pipeline, RawBsonDocument::class.java)
    }

    private fun clusterTime(event: ChangeStreamDocument<RawBsonDocument>): String =
        (event.clusterTime?.let { Instant.ofEpochSecond(it.time.toLong()) } ?: Instant.now())
            .toString()

    override fun checkpoint(): PartitionReadCheckpoint =
        PartitionReadCheckpoint(
            MongoDbCdcState.of(
                    resumeToken,
                    configuration.schemaEnforced,
                    cdcSyncedUntil,
                    prior = priorState,
                )
                .toOpaqueStateValue(),
            numRecords,
            checkpointPartitionId,
        )

    companion object {
        /** Tags the change-stream cursor in `currentOp` / profiler output for operators. */
        const val STREAM_COMMENT = "airbyte-source-mongodb"
        /** HistoryLost, FatalError, InvalidResumeToken, FailedToParse, empty, bad KeyString. */
        val INVALID_RESUME_TOKEN_ERROR_CODES: Set<Int> = setOf(286, 280, 260, 9, 40649, 50811)
        const val CHANGE_STREAM_HISTORY_LOST = 286
        /**
         * Empty polls (about a second each, the server's await time) tolerated before the target is
         * reached: well past the 10 s periodic no-op that moves an idle shard's position.
         */
        const val MAX_EMPTY_POLLS = 60
        /** Namespaces listed by name in the start-of-read line before "and N more". */
        const val NAMESPACES_LOGGED = 20
    }
}
