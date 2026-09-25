/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class SlackHistoryStreamStateTest {

    private val id = StreamIdentifier.from(StreamDescriptor().withName("channel_messages"))

    @Test
    fun testLegacyPerPartitionChannelMessagesState() {
        val state =
            SlackHistoryStreamState.parse(
                id,
                Jsons.readTree(
                    """{"use_global_cursor": false,
                        "states": [{"partition": {"channel": "C1", "parent_slice": {}}, "cursor": {"float_ts": "1683104542.931169"}},
                                   {"partition": {"channel_id": "C2", "parent_slice": {}}, "cursor": {"float_ts": 2534945416.0}}],
                        "state": {"float_ts": "2534945416.0"}, "lookback_window": 0}""",
                ),
            )
        Assertions.assertEquals(1683104542.931169, state.cursorOf("C1"))
        Assertions.assertEquals(2534945416.0, state.cursorOf("C2"))
        Assertions.assertNull(
            state.cursorOf("C3"),
            "a channel without an entry starts from start_date"
        )
        Assertions.assertEquals(2534945416.0, state.globalCursor)
        Assertions.assertFalse(state.interrupted)
        Assertions.assertNull(state.syncStart)
    }

    @Test
    fun testLegacyGlobalCursorAppliesToEveryChannel() {
        val state =
            SlackHistoryStreamState.parse(
                id,
                Jsons.readTree(
                    """{"use_global_cursor": true, "states": [], "state": {"float_ts": "1700000000.0"}}"""
                ),
            )
        Assertions.assertEquals(1700000000.0, state.cursorOf("C-any"))
    }

    @Test
    fun testFlatLegacyState() {
        val state =
            SlackHistoryStreamState.parse(id, Jsons.readTree("""{"float_ts": 1700000000}"""))
        Assertions.assertEquals(1700000000.0, state.cursorOf("C1"))
    }

    /** Legacy threads partitions are thread parents; their cursors collapse to the maximum. */
    @Test
    fun testLegacyThreadsState() {
        val state =
            SlackHistoryStreamState.parse(
                StreamIdentifier.from(StreamDescriptor().withName("threads")),
                Jsons.readTree(
                    """{"states": [
                          {"partition": {"float_ts": "1683104542.931169", "parent_slice": {"channel": "C1", "parent_slice": {}}}, "cursor": {"float_ts": "1753263869"}},
                          {"partition": {"float_ts": "1683104600.000000", "parent_slice": {"channel": "C1", "parent_slice": {}}}, "cursor": {"float_ts": "1753263999"}}],
                        "state": {"float_ts": "1626984010"},
                        "parent_state": {"channel_messages": {"float_ts": 1753177470.0}}}""",
                ),
            )
        Assertions.assertTrue(state.channelCursors.isEmpty())
        // `state.float_ts` wins when present, like the legacy connector's global cursor.
        Assertions.assertEquals(1626984010.0, state.globalCursor)
    }

    @Test
    fun testEmptyAndNull() {
        Assertions.assertSame(
            SlackHistoryStreamState.EMPTY,
            SlackHistoryStreamState.parse(id, null)
        )
        Assertions.assertSame(
            SlackHistoryStreamState.EMPTY,
            SlackHistoryStreamState.parse(id, Jsons.readTree("{}"))
        )
    }

    @Test
    fun testRoundTrip() {
        val emitted =
            SlackHistoryStreamState.emit(
                channelCursors = mapOf("C1" to 1700000000.0, "C2" to 1700000100.5),
                syncStart = 1700000100.5,
                lookbackSeconds = 86400,
                threads = false,
                done = setOf("C1"),
                progress =
                    SlackChannelProgress(
                        "C2",
                        1690000000.0,
                        1700000100.5,
                        "cursor",
                        1695000000.123456
                    ),
                watermark = 1690000000.0,
            )
        Assertions.assertEquals("1700000000.0", emitted["states"][0]["cursor"]["float_ts"].asText())
        Assertions.assertEquals("1700000100.5", emitted["state"]["float_ts"].asText())
        Assertions.assertEquals(false, emitted["use_global_cursor"].asBoolean())
        val parsed = SlackHistoryStreamState.parse(id, emitted)
        Assertions.assertEquals(
            mapOf("C1" to 1700000000.0, "C2" to 1700000100.5),
            parsed.channelCursors
        )
        Assertions.assertEquals(1700000100.5, parsed.syncStart)
        Assertions.assertEquals(setOf("C1"), parsed.done)
        Assertions.assertEquals(
            SlackChannelProgress("C2", 1690000000.0, 1700000100.5, "cursor", 1695000000.123456),
            parsed.progress
        )
        Assertions.assertEquals(1690000000.0, parsed.watermark)
        Assertions.assertTrue(parsed.interrupted)
    }

    @Test
    fun testThreadsShape() {
        val emitted =
            SlackHistoryStreamState.emit(
                channelCursors = mapOf("*" to 1700000100.5),
                syncStart = 1700000100.5,
                lookbackSeconds = 3600,
                threads = true,
                done = emptySet(),
                progress = null,
                watermark = 1700000100.5,
            )
        Assertions.assertEquals("1700000100", emitted["state"]["float_ts"].asText())
        Assertions.assertEquals(true, emitted["use_global_cursor"].asBoolean())
        Assertions.assertEquals(
            1700000100.0 - 3600,
            emitted["parent_state"]["channel_messages"]["float_ts"].asDouble()
        )
    }

    @Test
    fun testGarbageIsAConfigError() {
        Assertions.assertThrows(ConfigErrorException::class.java) {
            SlackHistoryStreamState.parse(id, Jsons.readTree("""{"states": "not a list"}"""))
        }
    }

    @Test
    fun testLegacyFloatFormatting() {
        Assertions.assertEquals("1683104542.931169", SlackTs.toLegacyFloatString(1683104542.931169))
        Assertions.assertEquals("1683104542.0", SlackTs.toLegacyFloatString(1683104542.0))
        Assertions.assertEquals("1683104542", SlackTs.toLegacyIntString(1683104542.931169))
        Assertions.assertEquals("1683104542.931169", SlackTs.toRequestParam(1683104542.931169))
        Assertions.assertEquals(
            "1683104542.931169",
            SlackTs.floatTsNode("1683104542.931169").toString()
        )
    }
}
