/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform.data

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class ValidationResultHandlerTest {

    @Test
    fun testHandleValidationResult() {
        val stream = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val abValue = StringValue("test value")
        val enrichedValue =
            EnrichedAirbyteValue(
                abValue = abValue,
                type = StringType,
                name = "testField",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val handler = ValidationResultHandler(mockk(relaxed = true))

        assertEquals(enrichedValue, handler.handle(stream, ValidationResult.Valid, enrichedValue))
        assertEquals(
            NullValue,
            handler
                .handle(
                    stream,
                    ValidationResult.ShouldNullify(Reason.DESTINATION_SERIALIZATION_ERROR),
                    enrichedValue
                )
                .abValue
        )

        val truncatedValue = StringValue("This is...")
        assertEquals(
            truncatedValue,
            handler
                .handle(
                    stream,
                    ValidationResult.ShouldTruncate(
                        truncatedValue,
                        Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    ),
                    enrichedValue
                )
                .abValue
        )
    }

    @Test
    fun testNullify() {
        val stream = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val abValue = StringValue("test value")
        val enrichedValue =
            EnrichedAirbyteValue(
                abValue = abValue,
                type = StringType,
                name = "testField",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val handler = ValidationResultHandler(mockk(relaxed = true))
        val nullifiedValue = handler.nullify(stream, enrichedValue)
        assertEquals(NullValue, nullifiedValue.abValue)
        assertEquals(1, nullifiedValue.changes.size)
        assertEquals(Change.NULLED, nullifiedValue.changes.first().change)
    }

    @Test
    fun testTruncate() {
        val stream = DestinationStream.Descriptor(namespace = "namespace", name = "name")
        val abValue = StringValue("This is a very long string that needs truncation")
        val enrichedValue =
            EnrichedAirbyteValue(
                abValue = abValue,
                type = StringType,
                name = "testField",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val newValue = StringValue("This is a...")
        val handler = ValidationResultHandler(mockk(relaxed = true))
        val truncatedValue = handler.truncate(stream, enrichedValue, newValue)
        assertEquals(newValue, truncatedValue.abValue)
        assertEquals(1, truncatedValue.changes.size)
        assertEquals(Change.TRUNCATED, truncatedValue.changes.first().change)
    }
}
