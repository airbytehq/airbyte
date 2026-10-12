/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DynamoDbStreamStateValueTest {

    private val streamID: StreamIdentifier =
        StreamIdentifier.from(StreamDescriptor().withName("orders"))

    /** The `stream_state` the legacy connector (legacy Java CDK `DbStreamState`) emitted. */
    @Test
    fun testParsesLegacyState() {
        val legacy =
            """
            {"stream_name":"orders","stream_namespace":null,"cursor_field":["updated_at"],
             "cursor":"2024-05-01T10:00:00Z","cursor_record_count":3}
            """
        val state: DynamoDbStreamStateValue =
            DynamoDbStreamStateValue.parse(streamID, Jsons.readTree(legacy))!!
        Assertions.assertEquals(listOf("updated_at"), state.cursorField)
        Assertions.assertEquals("2024-05-01T10:00:00Z", state.cursor)
        Assertions.assertEquals(3L, state.cursorRecordCount)
        Assertions.assertNull(state.scan)
        Assertions.assertNull(state.scanComplete)
    }

    /** A legacy stream whose items never had the cursor attribute: `cursor` is null. */
    @Test
    fun testParsesLegacyStateWithoutCursorValue() {
        val legacy = """{"stream_name":"orders","cursor_field":["updated_at"],"cursor":null}"""
        val state: DynamoDbStreamStateValue =
            DynamoDbStreamStateValue.parse(streamID, Jsons.readTree(legacy))!!
        Assertions.assertEquals(listOf("updated_at"), state.cursorField)
        Assertions.assertNull(state.cursor)
        Assertions.assertNull(state.cursorRecordCount)
    }

    @Test
    fun testNoState() {
        Assertions.assertNull(DynamoDbStreamStateValue.parse(streamID, null))
        Assertions.assertNull(DynamoDbStreamStateValue.parse(streamID, Jsons.nullNode()))
    }

    @Test
    fun testCompletedIncrementalStateHasLegacyShape() {
        val state =
            DynamoDbStreamStateValue(
                cursorField = listOf("updated_at"),
                cursor = "2024-05-02T00:00:00Z",
                cursorRecordCount = 1L,
            )
        Assertions.assertEquals(
            Jsons.readTree(
                """{"cursor_field":["updated_at"],"cursor":"2024-05-02T00:00:00Z","cursor_record_count":1}"""
            ),
            state.toOpaqueStateValue(),
        )
    }

    @Test
    fun testInProgressStateRoundTrip() {
        val state =
            DynamoDbStreamStateValue(
                cursorField = listOf("v"),
                cursor = "100",
                scan =
                    DynamoDbStreamStateValue.ScanProgress(
                        exclusiveStartKey =
                            Jsons.readTree("""{"pk":{"S":"a"},"sk":{"N":"1.5"}}""")
                                as com.fasterxml.jackson.databind.node.ObjectNode,
                        maxCursor = "250",
                        maxCursorRecordCount = 2L,
                    ),
            )
        val json = state.toOpaqueStateValue()
        Assertions.assertEquals(
            Jsons.readTree(
                """{"cursor_field":["v"],"cursor":"100",
                    "scan":{"exclusive_start_key":{"pk":{"S":"a"},"sk":{"N":"1.5"}},"max_cursor":"250","max_cursor_record_count":2}}"""
            ),
            json,
        )
        Assertions.assertEquals(state, DynamoDbStreamStateValue.parse(streamID, json))
    }

    @Test
    fun testFullRefreshCompleteState() {
        Assertions.assertEquals(
            Jsons.readTree("""{"scan_complete":true}"""),
            DynamoDbStreamStateValue.FULL_REFRESH_COMPLETE.toOpaqueStateValue(),
        )
    }

    @Test
    fun testSegmentedInProgressStateRoundTrip() {
        val key = Jsons.readTree("""{"pk":{"S":"a"},"sk":{"N":"7"}}""") as ObjectNode
        val state =
            DynamoDbStreamStateValue(
                cursorField = listOf("v"),
                cursor = "100",
                cursorRecordCount = 2L,
                scan =
                    DynamoDbStreamStateValue.ScanProgress(
                        totalSegments = 3,
                        segments =
                            listOf(
                                DynamoDbStreamStateValue.SegmentProgress(0, key, null, "250", 1L),
                                DynamoDbStreamStateValue.SegmentProgress(1, null, true, "300", 2L),
                                DynamoDbStreamStateValue.SegmentProgress(2),
                            ),
                    ),
            )
        val json = state.toOpaqueStateValue()
        Assertions.assertEquals(
            Jsons.readTree(
                """{"cursor_field":["v"],"cursor":"100","cursor_record_count":2,
                    "scan":{"total_segments":3,"segments":[
                      {"segment":0,"exclusive_start_key":{"pk":{"S":"a"},"sk":{"N":"7"}},"max_cursor":"250","max_cursor_record_count":1},
                      {"segment":1,"complete":true,"max_cursor":"300","max_cursor_record_count":2},
                      {"segment":2}]}}"""
            ),
            json,
        )
        val parsed: DynamoDbStreamStateValue = DynamoDbStreamStateValue.parse(streamID, json)!!
        Assertions.assertEquals(state, parsed)
        Assertions.assertEquals(3, parsed.scan!!.segmentCount())
        Assertions.assertEquals(state.scan!!.segments, parsed.scan!!.segmentProgress())
    }

    /** The shape written before tables were split into segments reads as segment 0 of 1. */
    @Test
    fun testSingleSegmentShapeReadsAsOneSegment() {
        val json =
            Jsons.readTree(
                """{"cursor_field":["v"],"cursor":"100",
                    "scan":{"exclusive_start_key":{"id":{"S":"a"}},"max_cursor":"250","max_cursor_record_count":2}}"""
            )
        val parsed: DynamoDbStreamStateValue = DynamoDbStreamStateValue.parse(streamID, json)!!
        Assertions.assertEquals(1, parsed.scan!!.segmentCount())
        Assertions.assertEquals(
            listOf(
                DynamoDbStreamStateValue.SegmentProgress(
                    0,
                    Jsons.readTree("""{"id":{"S":"a"}}""") as ObjectNode,
                    null,
                    "250",
                    2L,
                )
            ),
            parsed.scan!!.segmentProgress(),
        )
        val fullRefresh: DynamoDbStreamStateValue =
            DynamoDbStreamStateValue.parse(
                streamID,
                Jsons.readTree("""{"scan":{"exclusive_start_key":{"id":{"S":"a"}}}}"""),
            )!!
        Assertions.assertEquals(1, fullRefresh.scan!!.segmentProgress()!!.size)
        Assertions.assertNull(fullRefresh.scan!!.segmentProgress()!![0].maxCursor)
    }

    @Test
    fun testEmptyScanProgressHasNoSegments() {
        val parsed: DynamoDbStreamStateValue =
            DynamoDbStreamStateValue.parse(streamID, Jsons.readTree("""{"scan":{}}"""))!!
        Assertions.assertNull(parsed.scan!!.segmentProgress())
    }

    @Test
    fun testInconsistentSegmentsAreAConfigError() {
        for (bad in
            listOf(
                """{"scan":{"total_segments":2,"segments":[{"segment":0}]}}""",
                """{"scan":{"segments":[{"segment":1},{"segment":0}]}}""",
                """{"scan":{"segments":[{"segment":0},{"segment":0}]}}""",
            )) {
            val e =
                Assertions.assertThrows(
                    ConfigErrorException::class.java,
                    { DynamoDbStreamStateValue.parse(streamID, Jsons.readTree(bad)) },
                    "case: $bad",
                )
            Assertions.assertTrue(e.message!!.contains("orders"), e.message)
        }
    }

    @Test
    fun testUnreadableStateIsAConfigError() {
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                DynamoDbStreamStateValue.parse(
                    streamID,
                    Jsons.readTree("""{"scan":{"exclusive_start_key":"not a key"}}"""),
                )
            }
        Assertions.assertTrue(e.message!!.contains("orders"), e.message)
    }
}
