/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

/**
 * Tests for MSSQL stream state value serialization using JsonNode. These tests verify that state
 * values are stored as proper JsonNode types (following CDK best practices) rather than as strings.
 */
class MsSqlServerJdbcStreamStateValueTest {

    @Test
    fun `test cursorIncrementalCheckpoint stores JsonNode directly`() {
        val cursor = Field("numeric_cursor", BigDecimalFieldType)
        val checkpoint = Jsons.valueToTree<JsonNode>("123.45")

        val stateValue =
            MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(cursor, checkpoint)

        // Verify the cursor value is stored as JsonNode (not string)
        val deserialized =
            Jsons.treeToValue(stateValue, MsSqlServerJdbcStreamStateValue::class.java)
        assertNotNull(deserialized.cursor)
        assertEquals("123.45", deserialized.cursor!!.asText())
        assertEquals(listOf("numeric_cursor"), deserialized.cursorField)
    }

    @Test
    fun `test cursorIncrementalCheckpoint returns nullNode for null cursor`() {
        val cursor = Field("numeric_cursor", BigDecimalFieldType)
        val nullCheckpoint = Jsons.nullNode()

        val stateValue =
            MsSqlServerJdbcStreamStateValue.cursorIncrementalCheckpoint(cursor, nullCheckpoint)

        // Verify the function returns null node when cursor is null (CDK pattern)
        assert(stateValue.isNull) { "State should be null node for null cursor checkpoint" }
    }

    @Test
    fun `test snapshotCheckpoint stores JsonNode directly`() {
        val primaryKey = listOf(Field("id", IntFieldType))
        val checkpoint = listOf(Jsons.valueToTree<JsonNode>(42))

        val stateValue = MsSqlServerJdbcStreamStateValue.snapshotCheckpoint(primaryKey, checkpoint)

        // Verify the pk value is stored as JsonNode (not string)
        val deserialized =
            Jsons.treeToValue(stateValue, MsSqlServerJdbcStreamStateValue::class.java)
        assertNotNull(deserialized.pkValue)
        assertEquals(42, deserialized.pkValue!!.asInt())
        assertEquals("id", deserialized.pkName)
    }

    @Test
    fun `test snapshotCheckpoint returns nullNode for null pk`() {
        val primaryKey = listOf(Field("id", IntFieldType))
        val nullCheckpoint = listOf(Jsons.nullNode())

        val stateValue =
            MsSqlServerJdbcStreamStateValue.snapshotCheckpoint(primaryKey, nullCheckpoint)

        // Verify the function returns null node when pk checkpoint is null (CDK pattern)
        assert(stateValue.isNull) { "State should be null node for null pk checkpoint" }
    }

    @Test
    fun `test snapshotWithCursorCheckpoint stores JsonNode with incremental state`() {
        val primaryKey = listOf(Field("id", IntFieldType))
        val cursor = Field("updated_at", BigDecimalFieldType)
        val checkpoint = listOf(Jsons.valueToTree<JsonNode>(100))

        val stateValue =
            MsSqlServerJdbcStreamStateValue.snapshotWithCursorCheckpoint(
                primaryKey,
                checkpoint,
                cursor
            )

        // Verify pk value is stored as JsonNode and incremental state is embedded
        val deserialized =
            Jsons.treeToValue(stateValue, MsSqlServerJdbcStreamStateValue::class.java)
        assertNotNull(deserialized.pkValue)
        assertEquals(100, deserialized.pkValue!!.asInt())
        assertEquals("id", deserialized.pkName)
        assertEquals(StateType.PRIMARY_KEY.stateType, deserialized.stateType)

        // Verify incremental state is present and correctly structured
        assertNotNull(deserialized.incrementalState)
        val incrementalState =
            Jsons.treeToValue(
                deserialized.incrementalState,
                MsSqlServerJdbcStreamStateValue::class.java
            )
        assertEquals(listOf("updated_at"), incrementalState.cursorField)
    }
}
