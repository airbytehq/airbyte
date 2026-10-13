/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import java.time.Instant

/**
 * Per-stream state of a table read through the Storage Read API, for example:
 * ```
 * {"bigquery_read_session":{"name":"projects/p/locations/us/sessions/CAIS…",
 *                           "expires_at":"2026-09-22T10:28:18Z",
 *                           "bigquery_read_streams":["projects/p/locations/us/sessions/CAIS…/streams/GgJq…", …]},
 *  "bigquery_read_streams_completed_through":1,
 *  "bigquery_read_streams_complete":[3],
 *  "bigquery_read_stream_offsets":{"2":1300000},
 *  "bigquery_read_snapshot_time":"2026-09-22T04:28:16.000000Z",
 *  "bigquery_read_cursor_upper_bound":{"cursor":"updated_at","value":"2024-01-10T20:53:31.000000"}}
 * ```
 * The last two fields are only present for the initial snapshot of an incremental stream: the
 * session was opened on the table as of [snapshotTime] and [cursorUpperBound] is the maximum cursor
 * value at that same instant, which becomes the stream's cursor checkpoint once every read stream
 * is complete.
 *
 * Read streams are numbered by their position in the session. [completedThrough] is the high
 * watermark: every read stream with an index up to it is complete. Above it, [complete] lists the
 * read streams already finished out of order and [offsets] the row offset reached in the ones still
 * in flight; a read stream absent from both has not started. A row offset can only cause rows to be
 * re-read, never skipped, so a stale offset costs duplicates, not data.
 *
 * The state is only meaningful until the session expires; after that a new session, which splits
 * the table differently, starts the table over.
 */
@JsonInclude(JsonInclude.Include.NON_EMPTY)
data class BigQueryReadApiState(
    @JsonProperty(SESSION) val session: Session,
    @JsonProperty(COMPLETED_THROUGH) val completedThrough: Int = -1,
    @JsonProperty(COMPLETE) val complete: List<Int> = emptyList(),
    @JsonProperty(OFFSETS) val offsets: Map<String, Long> = emptyMap(),
    @JsonProperty(SNAPSHOT_TIME) val snapshotTime: String? = null,
    @JsonProperty(CURSOR_UPPER_BOUND) val cursorUpperBound: CursorBound? = null,
) {
    /** The cursor column and its maximum value as of the session's snapshot time. */
    data class CursorBound(
        @JsonProperty("cursor") val cursor: String,
        @JsonProperty("value") val value: JsonNode,
    )

    data class Session(
        @JsonProperty("name") val name: String,
        @JsonProperty("expires_at") val expiresAt: String,
        @JsonProperty(READ_STREAMS) val readStreams: List<String> = emptyList(),
    ) {
        @get:JsonIgnore
        val expiresAtInstant: Instant
            get() = Instant.parse(expiresAt)
    }

    @get:JsonIgnore
    val readStreamCount: Int
        get() = session.readStreams.size

    @get:JsonIgnore
    val snapshotTimeInstant: Instant?
        get() = snapshotTime?.let { Instant.parse(it) }

    /** Every read stream is complete. */
    @get:JsonIgnore
    val isComplete: Boolean
        get() =
            (0 until readStreamCount).all { it <= completedThrough || it in complete } ||
                readStreamCount == 0

    fun isExpired(now: Instant): Boolean = !session.expiresAtInstant.isAfter(now)

    /** The read streams still to read, in index order, each with the offset to resume at. */
    fun remainingWork(): List<ReadStreamWork> =
        session.readStreams.mapIndexedNotNull { index, name ->
            if (index <= completedThrough || index in complete) null
            else ReadStreamWork(index, name, offsets[index.toString()] ?: 0L)
        }

    fun toOpaqueStateValue(): OpaqueStateValue = Jsons.valueToTree(this)

    /** A read stream to read, from [offset] (rows already read from it). */
    data class ReadStreamWork(val index: Int, val name: String, val offset: Long)

    companion object {
        const val SESSION = "bigquery_read_session"
        const val READ_STREAMS = "bigquery_read_streams"
        const val COMPLETED_THROUGH = "bigquery_read_streams_completed_through"
        const val COMPLETE = "bigquery_read_streams_complete"
        const val OFFSETS = "bigquery_read_stream_offsets"
        const val SNAPSHOT_TIME = "bigquery_read_snapshot_time"
        const val CURSOR_UPPER_BOUND = "bigquery_read_cursor_upper_bound"

        /** The state, or null when [opaqueStateValue] is not in this shape. */
        fun parseOrNull(opaqueStateValue: OpaqueStateValue?): BigQueryReadApiState? {
            if (opaqueStateValue == null || !opaqueStateValue.isObject) return null
            val session: JsonNode = opaqueStateValue.get(SESSION) ?: return null
            if (!session.isObject || !session.hasNonNull("name")) return null
            return try {
                Jsons.treeToValue(opaqueStateValue, BigQueryReadApiState::class.java)
            } catch (_: RuntimeException) {
                null
            }
        }

        fun of(session: BigQueryReadSession): Session =
            Session(session.name, session.expiresAt.toString(), session.readStreams)
    }
}
