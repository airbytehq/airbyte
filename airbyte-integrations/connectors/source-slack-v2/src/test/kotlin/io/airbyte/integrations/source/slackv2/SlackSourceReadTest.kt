/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.slackv2.SlackTestSupport.Expected
import io.airbyte.integrations.source.slackv2.SlackTestSupport.ReadResult
import io.airbyte.integrations.source.slackv2.SlackTestSupport.assertSameRecords
import io.airbyte.integrations.source.slackv2.SlackTestSupport.catalog
import io.airbyte.integrations.source.slackv2.SlackTestSupport.config
import io.airbyte.integrations.source.slackv2.SlackTestSupport.configured
import io.airbyte.integrations.source.slackv2.SlackTestSupport.read
import io.airbyte.integrations.source.slackv2.SlackTestSupport.streamState
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Isolated

/**
 * Runs READ against the fake Slack server: every stream's records against what the workspace holds
 * (computed the way the legacy connector would have emitted them), stream statuses, state shapes,
 * incremental runs, resuming an interrupted sync, legacy state, channel joining and skipping, the
 * page cache, checkpoints and rate limiting.
 */
/** Runs alone: the fake server, its request log and the system properties are shared state. */
@Isolated
class SlackSourceReadTest {

    @BeforeEach
    fun resetServer() {
        server.requests.clear()
        // Every test starts from the seeded memberships (joins change them).
        workspace.members.clear()
        FakeSlackData.generate(messagesPerChannel = MESSAGES_PER_CHANNEL).members.forEach { (k, v)
            ->
            workspace.members[k] = v.toMutableList()
        }
    }

    // ------------------------------------------------------------------ users / channels / members

    @Test
    fun testUsers() {
        val result: ReadResult =
            read(server, catalog(configured(discovered, "users", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        assertSameRecords(workspace.users, result.records("users"), "users")
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("users"))
        Assertions.assertEquals(Jsons.readTree("""{"complete":true}"""), result.lastState("users"))
    }

    @Test
    fun testChannelsDefaultListsPublicNonArchivedAndJoins() {
        val result: ReadResult =
            read(server, catalog(configured(discovered, "channels", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        val names: Set<String> = result.records("channels").map { it["name"].asText() }.toSet()
        Assertions.assertEquals(setOf("general", "random", "unjoined", "empty"), names)
        // Records are the listed objects: `is_member` as listed, no `members` array.
        val unjoined: JsonNode =
            result.records("channels").first { it["name"].asText() == "unjoined" }
        Assertions.assertFalse(unjoined["is_member"].asBoolean())
        Assertions.assertNull(unjoined["members"])
        Assertions.assertEquals(1, server.requestCount("conversations.join"))
        Assertions.assertEquals(
            FakeSlackData.UNJOINED_ID,
            server.requests.first { it.method == "conversations.join" }.params["channel"]
        )
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("channels"))
    }

    @Test
    fun testChannelsWithPrivateArchivedAndFilter() {
        val result: ReadResult =
            read(
                server,
                catalog(configured(discovered, "channels", SyncMode.FULL_REFRESH)),
                config(
                    server,
                    extra =
                        mapOf(
                            "include_private_channels" to true,
                            "include_archived_channels" to true,
                            "join_channels" to false,
                            "channel_filter" to
                                listOf("general", "secret-plans", "old-project", "does-not-exist"),
                        ),
                ),
            )
        result.assertNoErrors()
        Assertions.assertEquals(
            setOf("general", "secret-plans", "old-project"),
            result.records("channels").map { it["name"].asText() }.toSet()
        )
        Assertions.assertEquals(0, server.requestCount("conversations.join"))
        val list = server.requests.first { it.method == "conversations.list" }
        Assertions.assertEquals("public_channel,private_channel", list.params["types"])
        Assertions.assertEquals("false", list.params["exclude_archived"])
        Assertions.assertEquals("999", list.params["limit"])
    }

    @Test
    fun testChannelMembers() {
        val result: ReadResult =
            read(server, catalog(configured(discovered, "channel_members", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        val expected: List<JsonNode> =
            listOf(
                    FakeSlackData.GENERAL_ID,
                    FakeSlackData.RANDOM_ID,
                    FakeSlackData.UNJOINED_ID,
                    FakeSlackData.EMPTY_ID
                )
                .flatMap { channel ->
                    workspace.members[channel]!!.map {
                        Jsons.objectNode().put("member_id", it).put("channel_id", channel)
                    }
                }
        assertSameRecords(expected, result.records("channel_members"), "channel_members")
    }

    // ------------------------------------------------------------------ channel_messages

    @Test
    fun testChannelMessagesFullRefresh() {
        val result: ReadResult =
            read(server, catalog(configured(discovered, "channel_messages", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        val expected: List<JsonNode> =
            listOf(FakeSlackData.GENERAL_ID, FakeSlackData.RANDOM_ID, FakeSlackData.UNJOINED_ID)
                .flatMap { Expected.channelMessages(workspace, it, 0.0, Double.MAX_VALUE) }
        assertSameRecords(expected, result.records("channel_messages"), "channel_messages")
        val sample: JsonNode = result.records("channel_messages").first()
        Assertions.assertTrue(sample["float_ts"].isNumber)
        Assertions.assertEquals(sample["ts"].asText().toDouble(), sample["float_ts"].asDouble())
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("channel_messages"))
        // Requests: inclusive window from start_date, limit 999.
        val history = server.requests.first { it.method == "conversations.history" }
        Assertions.assertEquals("true", history.params["inclusive"])
        Assertions.assertEquals("999", history.params["limit"])
        Assertions.assertEquals(
            SlackTs.toRequestParam(SlackTestSupport.START_EPOCH),
            history.params["oldest"]
        )
    }

    @Test
    fun testChannelMessagesIncrementalStateAndSecondRun() {
        val first: ReadResult =
            read(server, catalog(configured(discovered, "channel_messages", SyncMode.INCREMENTAL)))
        first.assertNoErrors()
        val state: JsonNode = first.lastState("channel_messages")
        Assertions.assertEquals(false, state["use_global_cursor"].asBoolean())
        val cursors: Map<String, String> =
            state["states"].associate {
                it["partition"]["channel"].asText() to it["cursor"]["float_ts"].asText()
            }
        // Every channel that was read, the empty one included, ends the sync at the sync bound.
        Assertions.assertEquals(
            setOf(
                FakeSlackData.GENERAL_ID,
                FakeSlackData.RANDOM_ID,
                FakeSlackData.UNJOINED_ID,
                FakeSlackData.EMPTY_ID
            ),
            cursors.keys
        )
        Assertions.assertEquals(Jsons.objectNode(), state["states"][0]["partition"]["parent_slice"])
        Assertions.assertTrue(
            cursors.values.all { it.matches(Regex("\\d+\\.\\d+")) },
            "legacy float strings: $cursors"
        )
        Assertions.assertEquals(
            state["slack_v2"]["sync_start"].asDouble(),
            cursors.values.first().toDouble(),
            1e-6
        )
        Assertions.assertNull(state["slack_v2"]["done"])
        Assertions.assertNull(state["slack_v2"]["progress"])
        Assertions.assertEquals(state["slack_v2"]["sync_start"], state["slack_v2"]["watermark"])
        Assertions.assertEquals(0, state["lookback_window"].asInt())
        Assertions.assertEquals(
            first.records("channel_messages").size.toDouble(),
            first.stateMessages("channel_messages").last().sourceStats.recordCount
        )

        server.requests.clear()
        val second: ReadResult =
            read(
                server,
                catalog(configured(discovered, "channel_messages", SyncMode.INCREMENTAL)),
                state = listOf(streamState("channel_messages", state))
            )
        second.assertNoErrors()
        Assertions.assertEquals(0, second.records("channel_messages").size)
        // One history call per channel, from the saved cursor.
        val calls = server.requests.filter { it.method == "conversations.history" }
        Assertions.assertEquals(4, calls.size)
        Assertions.assertEquals(
            SlackTs.toRequestParam(state["slack_v2"]["sync_start"].asDouble()),
            calls.first().params["oldest"]
        )
        Assertions.assertTrue(
            second.lastState("channel_messages")["slack_v2"]["sync_start"].asDouble() >
                state["slack_v2"]["sync_start"].asDouble()
        )
    }

    @Test
    fun testChannelMessagesFromLegacyState() {
        // Cursor in the middle of general's history, as the legacy connector saved it.
        val general: List<ObjectNode> =
            Expected.channelMessages(workspace, FakeSlackData.GENERAL_ID, 0.0, Double.MAX_VALUE)
        val midTs: Double = general[general.size / 2]["ts"].asText().toDouble()
        val legacyState: String =
            """{"use_global_cursor": false, "lookback_window": 0,
                "states": [{"partition": {"channel": "${FakeSlackData.GENERAL_ID}", "parent_slice": {}}, "cursor": {"float_ts": "${SlackTs.toLegacyFloatString(midTs)}"}}],
                "state": {"float_ts": "${SlackTs.toLegacyFloatString(midTs)}"}}"""
        val result: ReadResult =
            read(
                server,
                catalog(configured(discovered, "channel_messages", SyncMode.INCREMENTAL)),
                config(server, extra = mapOf("channel_filter" to listOf("general", "random"))),
                state = listOf(streamState("channel_messages", legacyState)),
            )
        result.assertNoErrors()
        val expected: List<JsonNode> =
            Expected.channelMessages(workspace, FakeSlackData.GENERAL_ID, midTs, Double.MAX_VALUE) +
                Expected.channelMessages(workspace, FakeSlackData.RANDOM_ID, 0.0, Double.MAX_VALUE)
        assertSameRecords(
            expected,
            result.records("channel_messages"),
            "channel_messages from legacy state"
        )
    }

    @Test
    fun testLookbackWindowReReadsRecentMessages() {
        val general: List<ObjectNode> =
            Expected.channelMessages(workspace, FakeSlackData.GENERAL_ID, 0.0, Double.MAX_VALUE)
        val lastTs: Double = general.last()["ts"].asText().toDouble()
        val state =
            """{"states": [{"partition": {"channel": "${FakeSlackData.GENERAL_ID}", "parent_slice": {}}, "cursor": {"float_ts": "$lastTs"}}]}"""
        val result: ReadResult =
            read(
                server,
                catalog(configured(discovered, "channel_messages", SyncMode.INCREMENTAL)),
                config(
                    server,
                    extra = mapOf("channel_filter" to listOf("general"), "lookback_window" to 10)
                ),
                state = listOf(streamState("channel_messages", state)),
            )
        result.assertNoErrors()
        val expected: List<JsonNode> =
            Expected.channelMessages(
                workspace,
                FakeSlackData.GENERAL_ID,
                lastTs - 10 * 86400,
                Double.MAX_VALUE
            )
        Assertions.assertTrue(expected.size > 1)
        assertSameRecords(expected, result.records("channel_messages"), "lookback")
    }

    /** Small windows and a short checkpoint interval: several states, then the same records. */
    @Test
    fun testChannelMessagesWindowsAndCheckpoints() {
        val result: ReadResult =
            read(
                server,
                catalog(configured(discovered, "channel_messages", SyncMode.INCREMENTAL)),
                config(
                    server,
                    extra =
                        mapOf(
                            "channel_messages_window_size" to 7,
                            "checkpoint_target_interval_seconds" to 1
                        )
                ),
                properties =
                    mapOf(
                        SlackSharedState.HISTORY_PAGE_LIMIT_PROPERTY to "10",
                        SlackSharedState.RATE_LIMIT_SCALE_PROPERTY to "50"
                    ),
            )
        result.assertNoErrors()
        val expected: List<JsonNode> =
            listOf(FakeSlackData.GENERAL_ID, FakeSlackData.RANDOM_ID, FakeSlackData.UNJOINED_ID)
                .flatMap { Expected.channelMessages(workspace, it, 0.0, Double.MAX_VALUE) }
        assertSameRecords(expected, result.records("channel_messages"), "windows")
        val states: List<JsonNode> = result.states("channel_messages")
        Assertions.assertTrue(states.size > 1, "expected several checkpoints, got ${states.size}")
        Assertions.assertTrue(
            states.dropLast(1).any {
                it["slack_v2"]["progress"] != null || it["slack_v2"]["done"] != null
            }
        )
        Assertions.assertNull(states.last()["slack_v2"]["progress"])
        Assertions.assertTrue(server.requests.count { it.method == "conversations.history" } > 10)
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("channel_messages"))
    }

    /** An interrupted sync's state (done channels + progress in a page) resumes without gaps. */
    @Test
    fun testChannelMessagesResumesInterruptedSync() {
        val general: List<ObjectNode> =
            Expected.channelMessages(workspace, FakeSlackData.GENERAL_ID, 0.0, Double.MAX_VALUE)
        val resumeTs: Double = general[general.size / 3]["ts"].asText().toDouble()
        val syncStart: Double = general.last()["ts"].asText().toDouble() + 1.0
        val startDate: Double = SlackTestSupport.START_EPOCH
        val interrupted: String =
            """{"use_global_cursor": false,
                "states": [{"partition": {"channel": "${FakeSlackData.RANDOM_ID}", "parent_slice": {}}, "cursor": {"float_ts": "$syncStart"}}],
                "state": {"float_ts": "$syncStart"},
                "slack_v2": {"version": 1, "sync_start": $syncStart, "done": ["${FakeSlackData.RANDOM_ID}"],
                             "progress": {"channel": "${FakeSlackData.GENERAL_ID}", "window_oldest": $startDate, "window_latest": $syncStart, "page_resume_ts": $resumeTs}}}"""
        val result: ReadResult =
            read(
                server,
                catalog(configured(discovered, "channel_messages", SyncMode.INCREMENTAL)),
                config(server, extra = mapOf("channel_filter" to listOf("general", "random"))),
                state = listOf(streamState("channel_messages", interrupted)),
            )
        result.assertNoErrors()
        // general: the rest of the (newest-first) page below resumeTs; random: skipped as done.
        val expected: List<JsonNode> =
            Expected.channelMessages(workspace, FakeSlackData.GENERAL_ID, 0.0, resumeTs - 0.000001)
        assertSameRecords(expected, result.records("channel_messages"), "resume")
        Assertions.assertTrue(
            server.requests.none {
                it.method == "conversations.history" &&
                    it.params["channel"] == FakeSlackData.RANDOM_ID
            }
        )
        val finalState: JsonNode = result.lastState("channel_messages")
        Assertions.assertEquals(syncStart, finalState["slack_v2"]["sync_start"].asDouble())
        Assertions.assertNull(finalState["slack_v2"]["done"])
        Assertions.assertEquals(
            setOf(FakeSlackData.GENERAL_ID, FakeSlackData.RANDOM_ID),
            finalState["states"].map { it["partition"]["channel"].asText() }.toSet(),
        )
        Assertions.assertTrue(
            finalState["states"].all { it["cursor"]["float_ts"].asDouble() == syncStart }
        )
    }

    @Test
    fun testChannelMessagesSkipsChannelsTheBotIsNotIn() {
        val result: ReadResult =
            read(
                server,
                catalog(configured(discovered, "channel_messages", SyncMode.FULL_REFRESH)),
                config(server, extra = mapOf("join_channels" to false)),
            )
        result.assertNoErrors()
        val channels: Set<String> =
            result.records("channel_messages").map { it["channel_id"].asText() }.toSet()
        Assertions.assertEquals(setOf(FakeSlackData.GENERAL_ID, FakeSlackData.RANDOM_ID), channels)
        Assertions.assertEquals(0, server.requestCount("conversations.join"))
        Assertions.assertTrue(
            server.requests.none {
                it.method == "conversations.history" &&
                    it.params["channel"] == FakeSlackData.UNJOINED_ID
            }
        )
    }

    // ------------------------------------------------------------------ threads

    @Test
    fun testThreadsFullRefreshMatchesLegacyOutputWithFewerCalls() {
        val result: ReadResult =
            read(server, catalog(configured(discovered, "threads", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        val channels: List<String> =
            listOf(FakeSlackData.GENERAL_ID, FakeSlackData.RANDOM_ID, FakeSlackData.UNJOINED_ID)
        val expected: List<JsonNode> =
            channels.flatMap {
                Expected.threads(workspace, it, 0.0, Double.MAX_VALUE, ignoreNoReplies = false)
            }
        assertSameRecords(expected, result.records("threads"), "threads")
        val historyMessages: Int =
            channels.sumOf { Expected.channelMessages(workspace, it, 0.0, Double.MAX_VALUE).size }
        val threads: Int =
            channels.sumOf { c ->
                workspace.messages[c]!!.count { (it["reply_count"]?.asInt() ?: 0) > 0 }
            }
        val repliesCalls: Int = server.requestCount("conversations.replies")
        Assertions.assertEquals(
            threads,
            repliesCalls,
            "one replies call per thread (legacy: one per message, $historyMessages)"
        )
        Assertions.assertTrue(repliesCalls < historyMessages / 2)
        val state: JsonNode = result.lastState("threads")
        Assertions.assertEquals(true, state["use_global_cursor"].asBoolean())
        Assertions.assertTrue(state["state"]["float_ts"].asText().matches(Regex("\\d+")))
        Assertions.assertNotNull(state["parent_state"]["channel_messages"]["float_ts"])
    }

    @Test
    fun testThreadsIgnoreNoReplies() {
        val result: ReadResult =
            read(
                server,
                catalog(configured(discovered, "threads", SyncMode.FULL_REFRESH)),
                config(
                    server,
                    extra =
                        mapOf(
                            "threads_ignore_no_replies" to true,
                            "channel_filter" to listOf("general")
                        )
                ),
            )
        result.assertNoErrors()
        val expected: List<JsonNode> =
            Expected.threads(
                workspace,
                FakeSlackData.GENERAL_ID,
                0.0,
                Double.MAX_VALUE,
                ignoreNoReplies = true
            )
        assertSameRecords(expected, result.records("threads"), "threads ignore_no_replies")
        Assertions.assertTrue(result.records("threads").all { it["thread_ts"] != null })
    }

    /** Second incremental run: threads without new replies cost no call at all. */
    @Test
    fun testThreadsIncrementalSkipsUnchangedThreads() {
        val cfg = config(server, extra = mapOf("channel_filter" to listOf("general")))
        val first: ReadResult =
            read(server, catalog(configured(discovered, "threads", SyncMode.INCREMENTAL)), cfg)
        first.assertNoErrors()
        val state: JsonNode = first.lastState("threads")
        Assertions.assertTrue(server.requestCount("conversations.replies") > 0)

        server.requests.clear()
        val second: ReadResult =
            read(
                server,
                catalog(configured(discovered, "threads", SyncMode.INCREMENTAL)),
                cfg,
                state = listOf(streamState("threads", state))
            )
        second.assertNoErrors()
        Assertions.assertEquals(0, second.records("threads").size)
        Assertions.assertEquals(0, server.requestCount("conversations.replies"))
        Assertions.assertEquals(1, server.requestCount("conversations.history"))

        // With a lookback, the history is re-read but unchanged threads are still skipped.
        server.requests.clear()
        val third: ReadResult =
            read(
                server,
                catalog(configured(discovered, "threads", SyncMode.INCREMENTAL)),
                config(
                    server,
                    extra = mapOf("channel_filter" to listOf("general"), "lookback_window" to 365)
                ),
                state = listOf(streamState("threads", state)),
            )
        third.assertNoErrors()
        val expectedWithoutThreads: List<JsonNode> =
            Expected.threads(
                    workspace,
                    FakeSlackData.GENERAL_ID,
                    0.0,
                    Double.MAX_VALUE,
                    ignoreNoReplies = false
                )
                .filter { (it["reply_count"]?.asInt() ?: 0) == 0 && it["thread_ts"] == null }
        // Messages without replies are re-emitted (no call); every thread is skipped as unchanged.
        assertSameRecords(expectedWithoutThreads, third.records("threads"), "lookback threads")
        Assertions.assertEquals(0, server.requestCount("conversations.replies"))
    }

    /** A thread that got a new reply since the last sync is fetched again. */
    @Test
    fun testThreadsIncrementalFetchesThreadsWithNewReplies() {
        val cfg = config(server, extra = mapOf("channel_filter" to listOf("random")))
        val first: ReadResult =
            read(server, catalog(configured(discovered, "threads", SyncMode.INCREMENTAL)), cfg)
        first.assertNoErrors()
        val state: ObjectNode = first.lastState("threads").deepCopy()
        // Pretend the last completed sync started just before the newest reply of the channel:
        // only the thread that got that reply has something new.
        val threads: List<ObjectNode> =
            workspace.messages[FakeSlackData.RANDOM_ID]!!.filter {
                (it["reply_count"]?.asInt() ?: 0) > 0
            }
        val newestReply: Double = threads.maxOf { it["latest_reply"].asText().toDouble() }
        val watermark: Double = newestReply - 1.0
        val v2: ObjectNode = state["slack_v2"] as ObjectNode
        v2.put("watermark", watermark)
        v2.put("sync_start", watermark)
        (state["state"] as ObjectNode).put("float_ts", SlackTs.toLegacyIntString(watermark))
        server.requests.clear()
        // The lookback (60 days) brings every thread parent back into the scanned history.
        val second: ReadResult =
            read(
                server,
                catalog(configured(discovered, "threads", SyncMode.INCREMENTAL)),
                config(
                    server,
                    extra = mapOf("channel_filter" to listOf("random"), "lookback_window" to 60)
                ),
                state = listOf(streamState("threads", state)),
            )
        second.assertNoErrors()
        val refetched: Int = threads.count { it["latest_reply"].asText().toDouble() >= watermark }
        Assertions.assertTrue(refetched >= 1)
        Assertions.assertEquals(refetched, server.requestCount("conversations.replies"))
        val expectedThreads: List<JsonNode> =
            threads
                .filter { it["latest_reply"].asText().toDouble() >= watermark }
                .flatMap { parent ->
                    workspace.messages[FakeSlackData.RANDOM_ID]!!
                        .filter { it["ts"] == parent["ts"] || it["thread_ts"] == parent["ts"] }
                        .map { Expected.decorate(it, FakeSlackData.RANDOM_ID) }
                }
        val expectedPlain: List<JsonNode> =
            Expected.channelMessages(
                    workspace,
                    FakeSlackData.RANDOM_ID,
                    watermark - 60 * 86400,
                    Double.MAX_VALUE
                )
                .filter { (it["reply_count"]?.asInt() ?: 0) == 0 && it["thread_ts"] == null }
        assertSameRecords(
            expectedThreads + expectedPlain,
            second.records("threads"),
            "threads with new replies"
        )
    }

    @Test
    fun testThreadsFromLegacyStateFetchesEverything() {
        val random: List<ObjectNode> =
            Expected.channelMessages(workspace, FakeSlackData.RANDOM_ID, 0.0, Double.MAX_VALUE)
        val cursor: Long = random[random.size / 2]["ts"].asText().toDouble().toLong()
        val legacy: String =
            """{"states": [{"partition": {"float_ts": "${random[0]["ts"].asText()}", "parent_slice": {"channel": "${FakeSlackData.RANDOM_ID}", "parent_slice": {}}}, "cursor": {"float_ts": "$cursor"}}],
                "state": {"float_ts": "$cursor"}, "parent_state": {"channel_messages": {"float_ts": $cursor.0}}}"""
        val result: ReadResult =
            read(
                server,
                catalog(configured(discovered, "threads", SyncMode.INCREMENTAL)),
                config(server, extra = mapOf("channel_filter" to listOf("random"))),
                state = listOf(streamState("threads", legacy)),
            )
        result.assertNoErrors()
        val expected: List<JsonNode> =
            Expected.threads(
                workspace,
                FakeSlackData.RANDOM_ID,
                cursor.toDouble(),
                Double.MAX_VALUE,
                ignoreNoReplies = false
            )
        assertSameRecords(expected, result.records("threads"), "threads from legacy state")
        Assertions.assertTrue(
            result.records("threads").size <
                Expected.threads(workspace, FakeSlackData.RANDOM_ID, 0.0, Double.MAX_VALUE, false)
                    .size
        )
    }

    // ------------------------------------------------------------------ both streams, cache,
    // limits

    @Test
    fun testMessagesAndThreadsShareHistoryPages() {
        val result: ReadResult =
            read(
                server,
                catalog(
                    configured(discovered, "channel_messages", SyncMode.INCREMENTAL),
                    configured(discovered, "threads", SyncMode.INCREMENTAL)
                ),
                config(server, extra = mapOf("concurrency" to 2)),
            )
        result.assertNoErrors()
        val channels: List<String> =
            listOf(FakeSlackData.GENERAL_ID, FakeSlackData.RANDOM_ID, FakeSlackData.UNJOINED_ID)
        assertSameRecords(
            channels.flatMap { Expected.channelMessages(workspace, it, 0.0, Double.MAX_VALUE) },
            result.records("channel_messages"),
            "messages"
        )
        assertSameRecords(
            channels.flatMap { Expected.threads(workspace, it, 0.0, Double.MAX_VALUE, false) },
            result.records("threads"),
            "threads"
        )
        // Each history page was fetched once for both streams: one per channel read (the empty one
        // too).
        Assertions.assertEquals(channels.size + 1, server.requestCount("conversations.history"))
        Assertions.assertEquals(1, server.requestCount("conversations.list"))
    }

    @Test
    fun testRateLimitedServerStillCompletes() {
        // Two history requests per minute: the third page is only served after a 429 and a wait.
        val limited =
            FakeSlackServer(
                    workspace,
                    rateLimits = mapOf("conversations.history" to 2.0),
                    retryAfterSeconds = 1
                )
                .start()
        try {
            val result: ReadResult =
                read(
                    limited,
                    catalog(configured(discovered, "channel_messages", SyncMode.FULL_REFRESH)),
                    config(limited, extra = mapOf("channel_filter" to listOf("random"))),
                    // Real pacing (scale 1) and three pages of ten messages.
                    properties =
                        mapOf(
                            SlackSharedState.HISTORY_PAGE_LIMIT_PROPERTY to "10",
                            SlackSharedState.RATE_LIMIT_SCALE_PROPERTY to "1"
                        ),
                )
            result.assertNoErrors()
            assertSameRecords(
                Expected.channelMessages(workspace, FakeSlackData.RANDOM_ID, 0.0, Double.MAX_VALUE),
                result.records("channel_messages"),
                "messages under 429s"
            )
            Assertions.assertTrue(limited.rateLimitedCount.get() > 0, "the fake never answered 429")
            Assertions.assertEquals(
                3,
                limited.requests.count { it.method == "conversations.history" && it.status == 200 }
            )
        } finally {
            limited.stop()
        }
    }

    @Test
    fun testNonMarketplacePagesAreFollowed() {
        server.nonMarketplace = true
        try {
            val result: ReadResult =
                read(
                    server,
                    catalog(configured(discovered, "channel_messages", SyncMode.FULL_REFRESH)),
                    config(server, extra = mapOf("channel_filter" to listOf("random")))
                )
            result.assertNoErrors()
            assertSameRecords(
                Expected.channelMessages(workspace, FakeSlackData.RANDOM_ID, 0.0, Double.MAX_VALUE),
                result.records("channel_messages"),
                "15 per page"
            )
            Assertions.assertTrue(
                server.requestCount("conversations.history") >= MESSAGES_PER_CHANNEL / 4 / 15
            )
        } finally {
            server.nonMarketplace = false
        }
    }

    @Test
    fun testUnknownErrorFailsTheStream() {
        server.injectError("users.list", FakeSlackServer.InjectedError(200, "some_new_error"))
        val result: ReadResult =
            read(server, catalog(configured(discovered, "users", SyncMode.FULL_REFRESH)))
        Assertions.assertNotNull(result.failure)
        Assertions.assertTrue(
            result.errors.any { it.contains("unrecognized error: some_new_error") },
            result.errors.toString()
        )
        Assertions.assertEquals(listOf("STARTED", "INCOMPLETE"), result.statuses("users"))
    }

    companion object {
        const val MESSAGES_PER_CHANNEL = 120
        lateinit var workspace: FakeSlackWorkspace
        lateinit var server: FakeSlackServer
        lateinit var discovered: AirbyteCatalog

        @JvmStatic
        @BeforeAll
        fun startServer() {
            workspace = FakeSlackData.generate(messagesPerChannel = MESSAGES_PER_CHANNEL)
            server = FakeSlackServer(workspace).start()
            discovered = SlackTestSupport.discover(server)
        }

        @JvmStatic
        @AfterAll
        fun stopServer() {
            server.stop()
        }
    }
}
