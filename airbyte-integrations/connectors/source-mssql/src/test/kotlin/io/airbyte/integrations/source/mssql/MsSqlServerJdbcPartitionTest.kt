/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.DefaultJdbcSharedState
import io.airbyte.cdk.read.DefaultJdbcStreamState
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.StateManager
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.mockk
import java.time.OffsetDateTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Tests for MSSQL partition logic, specifically focusing on numeric type handling and null safety
 * fixes.
 */
class MsSqlServerJdbcPartitionTest {

    @Test
    fun `test stateValueToJsonNode converts NUMBER to BigDecimal`() {
        // This prevents precision loss and type mismatch issues
        val field = EmittedField("numericId", BigDecimalFieldType)

        // Convert state value "13" using NUMBER type
        val result = stateValueToJsonNode(field, "13")

        assertNotNull(result)
        assertEquals(13, result.decimalValue().toInt())
        // Verify it's BigDecimal by checking the node type
        assert(result.isBigDecimal) { "Expected BigDecimal node but got ${result.nodeType}" }
    }

    @Test
    fun `test stateValueToJsonNode handles large NUMERIC values without precision loss`() {
        // Test that large NUMERIC values don't lose precision when converted
        val field = EmittedField("largeNumericId", BigDecimalFieldType)
        val largeValue = "12345678901234567890"

        val result = stateValueToJsonNode(field, largeValue)

        assertNotNull(result)
        assertEquals(largeValue, result.decimalValue().toPlainString())
    }

    @Test
    fun `test stateValueToJsonNode handles decimal NUMERIC values`() {
        // Test that decimal NUMERIC values are preserved correctly
        val field = EmittedField("decimalValue", BigDecimalFieldType)
        val decimalValue = "123.456"

        val result = stateValueToJsonNode(field, decimalValue)

        assertNotNull(result)
        assertEquals(decimalValue, result.decimalValue().toPlainString())
    }

    @Test
    fun `test stateValueToJsonNode handles INTEGER values`() {
        // Test that INTEGER types work correctly
        val field = EmittedField("integerId", IntFieldType)

        val result = stateValueToJsonNode(field, "42")

        assertNotNull(result)
        assertEquals(42, result.bigIntegerValue().toInt())
    }

    @Test
    fun `test stateValueToJsonNode handles empty string for NUMBER`() {
        // Test that empty string returns null node
        val field = EmittedField("numericId", BigDecimalFieldType)

        val result = stateValueToJsonNode(field, "")

        assertNotNull(result)
        assert(result.isNull) { "Expected null node for empty string" }
    }

    @Test
    fun `test stateValueToJsonNode handles null for NUMBER`() {
        // Test that null string returns null node
        val field = EmittedField("numericId", BigDecimalFieldType)

        val result = stateValueToJsonNode(field, null)

        assertNotNull(result)
        assert(result.isNull) { "Expected null node for null string" }
    }

    @Test
    fun `test stateValueToJsonNode handles string null for NUMBER`() {
        // Test that the string "null" (not null value) returns null node
        // This can happen when JSON serialization converts null to string "null"
        val field = EmittedField("numericId", BigDecimalFieldType)

        val result = stateValueToJsonNode(field, "null")

        assertNotNull(result)
        assert(result.isNull) { "Expected null node for string 'null'" }
    }

    @Test
    fun `test stateValueToJsonNode handles string null for INTEGER`() {
        // Test that the string "null" (not null value) returns null node for INTEGER
        val field = EmittedField("integerId", IntFieldType)

        val result = stateValueToJsonNode(field, "null")

        assertNotNull(result)
        assert(result.isNull) { "Expected null node for string 'null'" }
    }

    // --- Regression tests for oncall#12592: datetime2(7) cursor boundary ---
    // source-mssql truncates datetime2(7) nanos to 6-digit microseconds. A
    // `cursor <= MAX(truncated)` ceiling excluded rows whose 7th fractional
    // digit made them greater than the truncated max.  The fix removes the
    // upper-bound ceiling entirely.

    companion object {
        private val selectQueryGenerator = MsSqlSourceOperations()

        private fun sharedState(): DefaultJdbcSharedState {
            val configSpec =
                MsSqlServerSourceConfigurationSpecification().apply {
                    host = "localhost"
                    port = 1433
                    username = "sa"
                    password = "Password123!"
                    database = "master"
                }
            configSpec.setIncrementalValue(UserDefinedCursor())
            val configFactory = MsSqlServerSourceConfigurationFactory()
            val configuration = configFactory.make(configSpec)
            val mockSelectQuerier = mockk<SelectQuerier>()
            return DefaultJdbcSharedState(
                configuration,
                mockSelectQuerier,
                DefaultJdbcConstants(),
                ConcurrencyResource(configuration),
                ResourceAcquirer(emptyList())
            )
        }

        private val datetimeField = EmittedField("updated_at", LocalDateTimeFieldType)

        private val datetimeStream =
            Stream(
                id =
                    StreamIdentifier.from(
                        StreamDescriptor().withNamespace("dbo").withName("campaign")
                    ),
                schema = setOf(datetimeField),
                configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
                configuredPrimaryKey = listOf(datetimeField),
                configuredCursor = datetimeField,
            )

        private fun streamFeedBootstrap(
            stream: Stream,
            incumbentStateValue: OpaqueStateValue? = null
        ) =
            StreamFeedBootstrap(
                outputConsumer = BufferingOutputConsumer(ClockFactory().fixed()),
                metaFieldDecorator =
                    object : MetaFieldDecorator {
                        override val globalCursor: MetaField? = null
                        override val globalMetaFields: Set<MetaField> = emptySet()

                        override fun decorateRecordData(
                            timestamp: OffsetDateTime,
                            globalStateValue: OpaqueStateValue?,
                            stream: Stream,
                            recordData: com.fasterxml.jackson.databind.node.ObjectNode
                        ) {}

                        override fun decorateRecordData(
                            timestamp: OffsetDateTime,
                            globalStateValue: OpaqueStateValue?,
                            stream: Stream,
                            recordData: NativeRecordPayload
                        ) {}
                    },
                stateManager =
                    StateManager(initialStreamStates = mapOf(stream to incumbentStateValue)),
                stream,
                DataChannelFormat.JSONL,
                DataChannelMedium.STDIO,
                8192,
                ClockFactory().fixed(),
            )

        private fun streamState(
            incumbentStateValue: OpaqueStateValue? = null
        ): DefaultJdbcStreamState {
            val shared = sharedState()
            return DefaultJdbcStreamState(
                shared,
                streamFeedBootstrap(datetimeStream, incumbentStateValue),
            )
        }
    }

    @Test
    fun `nonResumable cursor incremental query has no upper bound ceiling`() {
        val cursorLowerBound = Jsons.textNode("2026-04-23T12:54:31.693333")
        val state = streamState()
        // Simulate the upper bound that the connector would compute (truncated to 6 digits)
        state.cursorUpperBound = Jsons.textNode("2026-04-23T12:54:31.693333")

        val partition =
            MsSqlServerJdbcNonResumableCursorIncrementalPartition(
                selectQueryGenerator,
                state,
                datetimeField,
                cursorLowerBound,
                isLowerBoundIncluded = false,
            )

        val querySpec = partition.nonResumableQuerySpec
        val sql = selectQueryGenerator.generate(querySpec.optimize()).sql

        // The query must NOT contain a <= upper bound ceiling
        assertFalse(
            sql.contains("<="),
            "Query must not contain '<=' ceiling clause. " +
                "A ceiling would miss datetime2(7) rows whose 7th digit exceeds the " +
                "6-digit-truncated max. Got: $sql"
        )
        // The query must still have a > lower bound
        assertTrue(sql.contains(">"), "Query must contain '>' lower bound clause. Got: $sql")
    }

    @Test
    fun `nonResumable cursor incremental with cutoffTime uses Lesser instead of LesserOrEqual`() {
        val cursorLowerBound = Jsons.textNode("2026-04-23T12:54:31.693333")
        val cursorCutoffTime = Jsons.textNode("2026-06-07T00:00:00.000000")
        val state = streamState()
        state.cursorUpperBound = Jsons.textNode("2026-04-23T12:54:31.693333")

        val partition =
            MsSqlServerJdbcNonResumableCursorIncrementalPartition(
                selectQueryGenerator,
                state,
                datetimeField,
                cursorLowerBound,
                isLowerBoundIncluded = false,
                cursorCutoffTime = cursorCutoffTime,
            )

        val querySpec = partition.nonResumableQuerySpec
        val sql = selectQueryGenerator.generate(querySpec.optimize()).sql

        // With cutoffTime, predicate should be `cursor > lower AND cursor < cutoff`
        assertFalse(
            sql.contains("<="),
            "Query with cutoffTime must not contain '<=' ceiling. Got: $sql"
        )
        assertTrue(sql.contains(">"), "Query must contain '>' lower bound. Got: $sql")
        assertTrue(sql.contains("<"), "Query with cutoffTime must contain '<' cutoff. Got: $sql")
    }

    @Test
    fun `resumable cursor incremental partition has null upperBound`() {
        val cursorLowerBound = Jsons.textNode("2026-04-23T12:54:31.693333")
        val cursorUpperBound = Jsons.textNode("2026-04-23T12:54:31.693333")
        val state = streamState()
        state.cursorUpperBound = cursorUpperBound

        val partition =
            MsSqlServerJdbcCursorIncrementalPartition(
                selectQueryGenerator,
                state,
                datetimeField,
                cursorLowerBound,
                isLowerBoundIncluded = false,
                cursorUpperBound = cursorUpperBound,
            )

        assertNull(
            partition.upperBound,
            "CursorIncrementalPartition.upperBound must be null to avoid excluding " +
                "datetime2(7) rows whose 7th fractional digit exceeds the truncated max"
        )
    }
}
