/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class MsSqlServerStateMigrationTest {

    @Test
    fun `should parse new format state correctly`() {
        val newState =
            """
        {
            "cursor": "2024-01-01T00:00:00",
            "version": 3,
            "state_type": "cursor_based",
            "stream_name": "users",
            "cursor_field": ["created_at"],
            "stream_namespace": "dataset_1tb",
            "cursor_record_count": 0
        }
        """.trimIndent()

        val parsed = MsSqlServerStateMigration.parseStateValue(Jsons.readTree(newState))

        assertEquals("2024-01-01T00:00:00", parsed.cursor)
        assertEquals("cursor_based", parsed.stateType)
        assertEquals("users", parsed.streamName)
        assertEquals("dataset_1tb", parsed.streamNamespace)
        assertEquals(listOf("created_at"), parsed.cursorField)
        assertEquals(0, parsed.cursorRecordCount)
        assertEquals(MsSqlServerJdbcStreamStateValue.CURRENT_VERSION, parsed.version)
    }

    @Test
    fun `should migrate legacy OrderedColumnLoadStatus state correctly`() {
        val legacyOrderedColumnState =
            """
        {
            "version": 2,
            "state_type": "ordered_column",
            "ordered_col": "id",
            "ordered_col_val": "12345",
            "incremental_state": {
                "version": 2,
                "state_type": "cursor_based",
                "stream_name": "users",
                "stream_namespace": "dataset_1tb",
                "cursor_field": ["created_at"],
                "cursor": "2024-01-01T00:00:00",
                "cursor_record_count": 0
            }
        }
        """.trimIndent()

        val parsed =
            MsSqlServerStateMigration.parseStateValue(Jsons.readTree(legacyOrderedColumnState))

        // Should be converted to primary_key state
        assertEquals("primary_key", parsed.stateType)
        assertEquals("id", parsed.pkName)
        assertEquals("12345", parsed.pkValue)
        assertEquals(MsSqlServerJdbcStreamStateValue.CURRENT_VERSION, parsed.version)

        // Should preserve incremental state
        assertNotNull(parsed.incrementalState)
        val incrementalState =
            Jsons.treeToValue(parsed.incrementalState, MsSqlServerJdbcStreamStateValue::class.java)
        assertEquals("cursor_based", incrementalState.stateType)
        assertEquals("users", incrementalState.streamName)
        assertEquals("dataset_1tb", incrementalState.streamNamespace)
        assertEquals(listOf("created_at"), incrementalState.cursorField)
        assertEquals("2024-01-01T00:00:00", incrementalState.cursor)
    }

    @Test
    fun `should migrate legacy CursorBasedStatus state correctly`() {
        val legacyCursorState =
            """
        {
            "version": 2,
            "state_type": "cursor_based",
            "stream_name": "users",
            "stream_namespace": "dataset_1tb",
            "cursor_field": ["created_at"],
            "cursor": "2024-01-01T00:00:00",
            "cursor_record_count": 1
        }
        """.trimIndent()

        val parsed = MsSqlServerStateMigration.parseStateValue(Jsons.readTree(legacyCursorState))

        assertEquals("cursor_based", parsed.stateType)
        assertEquals("users", parsed.streamName)
        assertEquals("dataset_1tb", parsed.streamNamespace)
        assertEquals(listOf("created_at"), parsed.cursorField)
        assertEquals("2024-01-01T00:00:00", parsed.cursor)
        assertEquals(1, parsed.cursorRecordCount)
        assertEquals(MsSqlServerJdbcStreamStateValue.CURRENT_VERSION, parsed.version)
    }

    @Test
    fun `should detect OrderedColumnLoadStatus by field presence`() {
        val legacyStateWithoutStateType =
            """
        {
            "version": 2,
            "ordered_col": "id",
            "ordered_col_val": "12345"
        }
        """.trimIndent()

        val parsed =
            MsSqlServerStateMigration.parseStateValue(Jsons.readTree(legacyStateWithoutStateType))

        assertEquals("primary_key", parsed.stateType)
        assertEquals("id", parsed.pkName)
        assertEquals("12345", parsed.pkValue)
        assertEquals(MsSqlServerJdbcStreamStateValue.CURRENT_VERSION, parsed.version)
    }

    @Test
    fun `should detect CursorBasedStatus by field presence`() {
        val legacyStateWithoutStateType =
            """
        {
            "version": 2,
            "stream_name": "users",
            "cursor_field": ["created_at"],
            "cursor": "2024-01-01T00:00:00"
        }
        """.trimIndent()

        val parsed =
            MsSqlServerStateMigration.parseStateValue(Jsons.readTree(legacyStateWithoutStateType))

        assertEquals("cursor_based", parsed.stateType)
        assertEquals("users", parsed.streamName)
        assertEquals(listOf("created_at"), parsed.cursorField)
        assertEquals("2024-01-01T00:00:00", parsed.cursor)
        assertEquals(MsSqlServerJdbcStreamStateValue.CURRENT_VERSION, parsed.version)
    }

    @Test
    fun `should handle unknown state format gracefully`() {
        val unknownState =
            """
        {
            "unknown_field": "unknown_value"
        }
        """.trimIndent()

        val parsed = MsSqlServerStateMigration.parseStateValue(Jsons.readTree(unknownState))

        // Should return default state
        assertEquals("cursor_based", parsed.stateType)
        assertEquals("", parsed.cursor)
        assertEquals(MsSqlServerJdbcStreamStateValue.CURRENT_VERSION, parsed.version)
    }

    @Test
    fun `should migrate ordered column state without incremental_state`() {
        val legacyOrderedColumnState =
            """
        {
            "version": 2,
            "state_type": "ordered_column",
            "ordered_col": "id",
            "ordered_col_val": "12345"
        }
        """.trimIndent()

        val parsed =
            MsSqlServerStateMigration.parseStateValue(Jsons.readTree(legacyOrderedColumnState))

        assertEquals("primary_key", parsed.stateType)
        assertEquals("id", parsed.pkName)
        assertEquals("12345", parsed.pkValue)
        assertNull(parsed.incrementalState)
        assertEquals(MsSqlServerJdbcStreamStateValue.CURRENT_VERSION, parsed.version)
    }

    @Test
    fun `should handle null values in legacy state`() {
        val legacyStateWithNulls =
            """
        {
            "version": 2,
            "state_type": "cursor_based",
            "stream_name": null,
            "cursor_field": null,
            "cursor": null
        }
        """.trimIndent()

        val parsed = MsSqlServerStateMigration.parseStateValue(Jsons.readTree(legacyStateWithNulls))

        assertEquals("cursor_based", parsed.stateType)
        assertEquals("", parsed.streamName)
        assertEquals(emptyList<String>(), parsed.cursorField)
        assertEquals("", parsed.cursor)
        assertEquals(0, parsed.cursorRecordCount)
        assertEquals(MsSqlServerJdbcStreamStateValue.CURRENT_VERSION, parsed.version)
    }
}
