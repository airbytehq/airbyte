/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

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
