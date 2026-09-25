/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.time.Instant

/**
 * Slack message timestamps (`ts`) are strings of epoch seconds with microseconds
 * (`"1683104542.931169"`). The legacy connector's cursors are floats of them: `%s_as_float` strings
 * (`"1683104542.931169"`, `"1683104542.0"`) for channel_messages and integer-second strings
 * (`"1683104542"`) for threads, sometimes saved as JSON numbers. Ordering is done on doubles
 * (microsecond spacing is well within double precision at 2^31 seconds).
 */
object SlackTs {
    fun toDouble(ts: String): Double? = ts.trim().toDoubleOrNull()

    fun toDouble(node: JsonNode?): Double? =
        when {
            node == null || node.isNull -> null
            node.isNumber -> node.asDouble()
            node.isTextual -> toDouble(node.asText())
            else -> null
        }

    fun fromInstant(instant: Instant): Double = instant.epochSecond + instant.nano / 1_000_000_000.0

    /** The JSON number Slack's `ts` string denotes, exactly (`1683104542.931169`, not `1.68E9`). */
    fun floatTsNode(ts: String): JsonNode =
        try {
            Jsons.numberNode(BigDecimal(ts.trim()))
        } catch (_: NumberFormatException) {
            Jsons.nullNode()
        }

    /**
     * Python's `str(float(x))` for an epoch second value, the legacy `%s_as_float` cursor format:
     * shortest round-trip digits in plain notation, always with a fractional part
     * (`"1683104542.931169"`, `"1683104542.0"`).
     */
    fun toLegacyFloatString(value: Double): String {
        val plain: String = BigDecimal(value.toString()).toPlainString()
        return if (plain.contains('.')) plain else "$plain.0"
    }

    /** The legacy `%s` cursor format of the threads stream: whole seconds. */
    fun toLegacyIntString(value: Double): String = value.toLong().toString()

    /** `oldest`/`latest` request parameter: six decimals, like a Slack `ts`. */
    fun toRequestParam(value: Double): String = "%.6f".format(java.util.Locale.ROOT, value)
}

/**
 * Where an interrupted read of a channel's history stopped: the window being read, the cursor of
 * the page to fetch next, and, when the page was left half-way, the `ts` below which its messages
 * still have to be processed (history pages are newest first).
 */
data class SlackChannelProgress(
    val channel: String,
    val windowOldest: Double,
    val windowLatest: Double,
    val pageCursor: String? = null,
    val pageResumeTs: Double? = null,
) {
    fun toJson(): ObjectNode =
        Jsons.objectNode().apply {
            put("channel", channel)
            put("window_oldest", windowOldest)
            put("window_latest", windowLatest)
            pageCursor?.let { put("page_cursor", it) }
            pageResumeTs?.let { put("page_resume_ts", it) }
        }

    companion object {
        fun fromJson(node: JsonNode?): SlackChannelProgress? {
            if (node == null || !node.isObject) return null
            val channel: String = node.get("channel")?.asText() ?: return null
            return SlackChannelProgress(
                channel = channel,
                windowOldest = node.get("window_oldest")?.asDouble() ?: return null,
                windowLatest = node.get("window_latest")?.asDouble() ?: return null,
                pageCursor = node.get("page_cursor")?.asText()?.ifBlank { null },
                pageResumeTs = node.get("page_resume_ts")?.asDouble(),
            )
        }
    }
}

/**
 * The state of the channel_messages and threads streams.
 *
 * **Input.** Every shape the legacy connector ever saved is read: the per-partition envelope
 * (`states: [{partition: {channel | channel_id, parent_slice}, cursor: {float_ts}}]` for
 * channel_messages, `states: [{partition: {float_ts: <parent ts>, parent_slice: {channel}}, ...}]`
 * for threads, with `state.float_ts`, `use_global_cursor` and `parent_state`), and the flat
 * `{float_ts: X}` of the oldest versions. Cursors may be float strings, integer strings or numbers.
 * For threads, whose legacy partitions are individual thread parents, the per-partition cursors
 * collapse to their maximum, exactly as the legacy `ThreadsStateMigration` did.
 *
 * **Output.** The legacy envelope (one `states` entry per channel for channel_messages, a global
 * cursor for threads, `state.float_ts`, `lookback_window`, `parent_state`), plus a `slack_v2`
 * object with what this connector needs to resume: `sync_start` (the `latest` bound of the sync
 * and, once it completed, every channel's cursor), the `done` channels and the
 * [SlackChannelProgress] of an interrupted sync.
 */
data class SlackHistoryStreamState(
    /** Saved cursor (float seconds) per channel id. */
    val channelCursors: Map<String, Double>,
    /** The stream-level cursor (`state.float_ts` or the flat `float_ts`). */
    val globalCursor: Double?,
    val useGlobalCursor: Boolean,
    /** `slack_v2.sync_start`: the `latest` bound of the last sync this connector ran. */
    val syncStart: Double?,
    /** Channels completed by an interrupted sync (only meaningful with [syncStart]). */
    val done: Set<String>,
    val progress: SlackChannelProgress?,
    /** `slack_v2.watermark`: the bound of the last sync that ran to completion. */
    val watermark: Double? = null,
) {
    /** Whether this state describes a sync that did not run to completion. */
    val interrupted: Boolean
        get() = syncStart != null && (done.isNotEmpty() || progress != null)

    /** The saved cursor of a channel: its own entry, else the global one when it applies. */
    fun cursorOf(channel: String): Double? =
        channelCursors[channel]
            ?: if (useGlobalCursor || channelCursors.isEmpty()) globalCursor else null

    companion object {
        val EMPTY = SlackHistoryStreamState(emptyMap(), null, false, null, emptySet(), null, null)

        fun parse(
            streamID: StreamIdentifier,
            opaqueStateValue: OpaqueStateValue?
        ): SlackHistoryStreamState {
            if (opaqueStateValue == null || opaqueStateValue.isNull || opaqueStateValue.isEmpty) {
                return EMPTY
            }
            try {
                val root: ObjectNode = opaqueStateValue as ObjectNode
                require(root.get("states")?.let { it.isArray } ?: true) {
                    "'states' must be a list"
                }
                require(root.get(SLACK_V2)?.let { it.isObject } ?: true) {
                    "'$SLACK_V2' must be an object"
                }
                val perChannel = LinkedHashMap<String, Double>()
                var maxPartitionCursor: Double? = null
                root.get("states")?.forEach { entry: JsonNode ->
                    val cursor: Double =
                        SlackTs.toDouble(entry.get("cursor")?.get(SlackStream.FLOAT_TS))
                            ?: return@forEach
                    maxPartitionCursor = maxOf(maxPartitionCursor ?: cursor, cursor)
                    val partition: JsonNode = entry.get("partition") ?: return@forEach
                    // channel_messages partitions are {channel} (or the stale {channel_id});
                    // threads
                    // partitions are {float_ts: <parent ts>, parent_slice: {channel}}, which are
                    // not per-channel cursors and only contribute to the maximum.
                    if (partition.has(SlackStream.FLOAT_TS)) return@forEach
                    val channel: String =
                        partition.get("channel")?.asText()
                            ?: partition.get("channel_id")?.asText() ?: return@forEach
                    perChannel[channel] = maxOf(perChannel[channel] ?: cursor, cursor)
                }
                val globalCursor: Double? =
                    SlackTs.toDouble(root.get("state")?.get(SlackStream.FLOAT_TS))
                        ?: SlackTs.toDouble(root.get(SlackStream.FLOAT_TS))
                            ?: (if (perChannel.isEmpty()) maxPartitionCursor else null)
                val v2: JsonNode? = root.get(SLACK_V2)
                val done: Set<String> =
                    v2?.get("done")?.mapNotNull { it.asText()?.ifBlank { null } }?.toSet()
                        ?: emptySet()
                return SlackHistoryStreamState(
                    channelCursors = perChannel,
                    globalCursor = globalCursor,
                    useGlobalCursor = root.get("use_global_cursor")?.asBoolean() ?: false,
                    syncStart =
                        v2?.get("sync_start")
                            ?.also { require(it.isNumber) { "'sync_start' must be a number" } }
                            ?.asDouble(),
                    done = done,
                    progress = SlackChannelProgress.fromJson(v2?.get("progress")),
                    watermark = v2?.get("watermark")?.asDouble(),
                )
            } catch (e: Exception) {
                throw ConfigErrorException(
                    "The saved state of stream '$streamID' could not be read: ${e.message}. " +
                        "Clear the connection's data to reset the stream and retry.",
                    e,
                )
            }
        }

        const val SLACK_V2 = "slack_v2"
        const val VERSION = 1

        /**
         * Builds the state to emit.
         *
         * @param channelCursors every channel's cursor after this checkpoint (float seconds)
         * @param threads true for the threads stream: global cursor in whole seconds and a
         * `parent_state` for the channel_messages history it depends on, like the legacy connector
         */
        fun emit(
            channelCursors: Map<String, Double>,
            syncStart: Double,
            lookbackSeconds: Long,
            threads: Boolean,
            done: Set<String>,
            progress: SlackChannelProgress?,
            watermark: Double?,
        ): OpaqueStateValue {
            val root: ObjectNode = Jsons.objectNode()
            val maxCursor: Double = (channelCursors.values.maxOrNull() ?: syncStart)
            if (threads) {
                root.put("use_global_cursor", true)
                root.set<JsonNode>("states", Jsons.arrayNode())
                root.set<JsonNode>(
                    "state",
                    Jsons.objectNode()
                        .put(SlackStream.FLOAT_TS, SlackTs.toLegacyIntString(maxCursor)),
                )
                root.set<JsonNode>(
                    "parent_state",
                    Jsons.objectNode()
                        .set<JsonNode>(
                            SlackStream.CHANNEL_MESSAGES.streamName,
                            Jsons.objectNode()
                                .put(
                                    SlackStream.FLOAT_TS,
                                    maxCursor.toLong() - lookbackSeconds.toDouble()
                                ),
                        ),
                )
            } else {
                root.put("use_global_cursor", false)
                val states: ArrayNode = Jsons.arrayNode()
                for ((channel: String, cursor: Double) in channelCursors.toSortedMap()) {
                    states.add(
                        Jsons.objectNode().apply {
                            set<JsonNode>(
                                "partition",
                                Jsons.objectNode().apply {
                                    put("channel", channel)
                                    set<JsonNode>("parent_slice", Jsons.objectNode())
                                },
                            )
                            set<JsonNode>(
                                "cursor",
                                Jsons.objectNode()
                                    .put(SlackStream.FLOAT_TS, SlackTs.toLegacyFloatString(cursor)),
                            )
                        },
                    )
                }
                root.set<JsonNode>("states", states)
                root.set<JsonNode>(
                    "state",
                    Jsons.objectNode()
                        .put(SlackStream.FLOAT_TS, SlackTs.toLegacyFloatString(maxCursor)),
                )
            }
            root.put("lookback_window", lookbackSeconds)
            val v2: ObjectNode =
                Jsons.objectNode().put("version", VERSION).put("sync_start", syncStart)
            watermark?.let { v2.put("watermark", it) }
            if (done.isNotEmpty()) {
                val doneNode: ArrayNode = Jsons.arrayNode()
                done.sorted().forEach { doneNode.add(it) }
                v2.set<JsonNode>("done", doneNode)
            }
            progress?.let { v2.set<JsonNode>("progress", it.toJson()) }
            root.set<JsonNode>(SLACK_V2, v2)
            // Through text, so that the tree uses the same node types as a parsed state.
            return Jsons.readTree(Jsons.writeValueAsString(root))
        }
    }
}

/** State of a full-refresh-only stream (users, channels, channel_members) read to its end. */
object SlackFullRefreshState {
    private const val COMPLETE = "complete"

    val COMPLETE_STATE: OpaqueStateValue = Jsons.readTree("""{"$COMPLETE":true}""")

    fun isComplete(state: OpaqueStateValue?): Boolean = state?.get(COMPLETE)?.asBoolean() ?: false
}
