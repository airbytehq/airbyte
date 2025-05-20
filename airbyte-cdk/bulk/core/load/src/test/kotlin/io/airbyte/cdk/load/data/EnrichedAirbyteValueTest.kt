/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class EnrichedAirbyteValueTest {

    @Test
    fun `test nullify method sets value to NullValue and adds change`() {
        val initialValue = StringValue("test value")
        val type = StringType
        val name = "testField"

        val enriched = EnrichedAirbyteValue(initialValue, type, name, airbyteMetaField = null)
        enriched.nullify(Reason.DESTINATION_SERIALIZATION_ERROR)

        assertEquals(NullValue, enriched.abValue)
        assertEquals(1, enriched.changes.size)

        val change = enriched.changes[0]
        assertEquals(name, change.field)
        assertEquals(Change.NULLED, change.change)
        assertEquals(Reason.DESTINATION_SERIALIZATION_ERROR, change.reason)
    }

    @Test
    fun `test nullify with default reason`() {
        val initialValue = IntegerValue(42)
        val type = IntegerType
        val name = "testField"

        val enriched = EnrichedAirbyteValue(initialValue, type, name, airbyteMetaField = null)
        enriched.nullify()

        assertEquals(NullValue, enriched.abValue)
        assertEquals(1, enriched.changes.size)

        val change = enriched.changes[0]
        assertEquals(name, change.field)
        assertEquals(Change.NULLED, change.change)
        assertEquals(Reason.DESTINATION_SERIALIZATION_ERROR, change.reason)
    }

    @Test
    fun `test nullify with custom reason`() {
        val initialValue = BooleanValue(true)
        val type = BooleanType
        val name = "testField"

        val enriched = EnrichedAirbyteValue(initialValue, type, name, airbyteMetaField = null)
        enriched.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)

        assertEquals(NullValue, enriched.abValue)
        assertEquals(1, enriched.changes.size)

        val change = enriched.changes[0]
        assertEquals(name, change.field)
        assertEquals(Change.NULLED, change.change)
        assertEquals(Reason.DESTINATION_FIELD_SIZE_LIMITATION, change.reason)
    }

    @Test
    fun `test truncate method sets new value and adds change`() {
        val initialValue = StringValue("This is a very long string that needs truncation")
        val type = StringType
        val name = "testField"
        val truncatedValue = StringValue("This is a very...")

        val enriched = EnrichedAirbyteValue(initialValue, type, name, airbyteMetaField = null)
        enriched.truncate(Reason.DESTINATION_RECORD_SIZE_LIMITATION, truncatedValue)

        assertEquals(truncatedValue, enriched.abValue)
        assertEquals(1, enriched.changes.size)

        val change = enriched.changes[0]
        assertEquals(name, change.field)
        assertEquals(Change.TRUNCATED, change.change)
        assertEquals(Reason.DESTINATION_RECORD_SIZE_LIMITATION, change.reason)
    }

    @Test
    fun `test truncate with default reason`() {
        val initialValue = StringValue("This is a very long string that needs truncation")
        val type = StringType
        val name = "testField"
        val truncatedValue = StringValue("This is a very...")

        val enriched = EnrichedAirbyteValue(initialValue, type, name, airbyteMetaField = null)
        enriched.truncate(newValue = truncatedValue)

        assertEquals(truncatedValue, enriched.abValue)
        assertEquals(1, enriched.changes.size)

        val change = enriched.changes[0]
        assertEquals(name, change.field)
        assertEquals(Change.TRUNCATED, change.change)
        assertEquals(Reason.DESTINATION_RECORD_SIZE_LIMITATION, change.reason)
    }

    @Test
    fun `test truncate with custom reason`() {
        val initialValue = StringValue("This is a very long string that needs truncation")
        val type = StringType
        val name = "testField"
        val truncatedValue = StringValue("This is a very...")

        val enriched = EnrichedAirbyteValue(initialValue, type, name, airbyteMetaField = null)
        enriched.truncate(Reason.DESTINATION_SERIALIZATION_ERROR, truncatedValue)

        assertEquals(truncatedValue, enriched.abValue)
        assertEquals(1, enriched.changes.size)

        val change = enriched.changes[0]
        assertEquals(name, change.field)
        assertEquals(Change.TRUNCATED, change.change)
        assertEquals(Reason.DESTINATION_SERIALIZATION_ERROR, change.reason)
    }

    @Test
    fun `test multiple changes are accumulated`() {
        val initialValue = StringValue("Initial value")
        val type = StringType
        val name = "testField"

        val enriched = EnrichedAirbyteValue(initialValue, type, name, airbyteMetaField = null)

        // First change - truncate
        val truncatedValue = StringValue("Init...")
        enriched.truncate(Reason.DESTINATION_RECORD_SIZE_LIMITATION, truncatedValue)

        // Second change - nullify
        enriched.nullify(Reason.DESTINATION_SERIALIZATION_ERROR)

        // Verify final state
        assertEquals(NullValue, enriched.abValue)
        assertEquals(2, enriched.changes.size)

        // First change
        val change1 = enriched.changes[0]
        assertEquals(name, change1.field)
        assertEquals(Change.TRUNCATED, change1.change)
        assertEquals(Reason.DESTINATION_RECORD_SIZE_LIMITATION, change1.reason)

        // Second change
        val change2 = enriched.changes[1]
        assertEquals(name, change2.field)
        assertEquals(Change.NULLED, change2.change)
        assertEquals(Reason.DESTINATION_SERIALIZATION_ERROR, change2.reason)
    }
}
