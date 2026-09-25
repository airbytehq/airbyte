/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.bigqueryv2.BigQueryBigNumericFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryDateTimeFieldType
import io.airbyte.integrations.source.bigqueryv2.BigQueryLegacyStreamState
import io.airbyte.integrations.source.bigqueryv2.BigQueryLongFieldType
import java.math.BigDecimal
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * The state an incremental initial snapshot emits once every read stream is complete must be the
 * `extract-jdbc` toolkit's cursor checkpoint, byte for byte, so that the next sync continues on the
 * query API's delta path. `BigQuerySourceReadTest.testIncrementalThenResume` (emulator) shows that
 * path emitting and resuming from exactly this shape:
 * `{"primary_key":{},"cursors":{"updated_at":"2024-01-03T00:00:00.000000Z"}}`.
 */
class BigQueryReadApiTerminalStateTest {

    private fun terminal(cursor: EmittedField, value: JsonNode): OpaqueStateValue =
        DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(cursor, value)

    @Test
    fun testTerminalStateIsTheToolkitCursorCheckpointForEveryCursorType() {
        val cases: List<Triple<EmittedField, JsonNode, String>> =
            listOf(
                Triple(
                    EmittedField("id", BigQueryLongFieldType),
                    Jsons.numberNode(4242L),
                    """{"primary_key":{},"cursors":{"id":4242}}""",
                ),
                Triple(
                    EmittedField("ts", OffsetDateTimeFieldType),
                    Jsons.textNode("2024-01-03T00:00:00.000000Z"),
                    """{"primary_key":{},"cursors":{"ts":"2024-01-03T00:00:00.000000Z"}}""",
                ),
                Triple(
                    EmittedField("updated_at", BigQueryDateTimeFieldType),
                    Jsons.textNode("2024-01-10T20:53:31.000000"),
                    """{"primary_key":{},"cursors":{"updated_at":"2024-01-10T20:53:31.000000"}}""",
                ),
                Triple(
                    EmittedField("price", BigDecimalFieldType),
                    Jsons.numberNode(BigDecimal("12345.6789")),
                    """{"primary_key":{},"cursors":{"price":12345.6789}}""",
                ),
                Triple(
                    EmittedField("big", BigQueryBigNumericFieldType),
                    Jsons.numberNode(BigDecimal("5500000000000000000000000000000")),
                    """{"primary_key":{},"cursors":{"big":5500000000000000000000000000000}}""",
                ),
            )
        for ((cursor, value, expected) in cases) {
            val state: OpaqueStateValue = terminal(cursor, value)
            Assertions.assertEquals(expected, Jsons.writeValueAsString(state), cursor.id)
            // The toolkit parses it back as a cursor checkpoint without a primary key ...
            val parsed: DefaultJdbcStreamStateValue =
                Jsons.treeToValue(state, DefaultJdbcStreamStateValue::class.java)
            Assertions.assertTrue(parsed.primaryKey.isEmpty(), cursor.id)
            Assertions.assertEquals(mapOf(cursor.id to value), parsed.cursors, cursor.id)
            // ... and neither the Read API state nor the legacy state parsers claim it.
            Assertions.assertNull(BigQueryReadApiState.parseOrNull(state), cursor.id)
            Assertions.assertNull(BigQueryLegacyStreamState.parseOrNull(state), cursor.id)
        }
    }

    @Test
    fun testCursorBoundValueIsCarriedVerbatimIntoTheTerminalState() {
        val cursor = EmittedField("updated_at", BigQueryDateTimeFieldType)
        val bound =
            BigQueryReadApiState.CursorBound(
                "updated_at",
                Jsons.textNode("2024-01-10T20:53:31.000000")
            )
        Assertions.assertEquals(
            Jsons.readTree(
                """{"primary_key":{},"cursors":{"updated_at":"2024-01-10T20:53:31.000000"}}"""
            ),
            terminal(cursor, bound.value),
        )
    }
}
