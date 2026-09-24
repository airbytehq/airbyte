/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.load

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.integrations.destination.postgres.write.transform.PostgresValueCoercer
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

internal class PostgresRecordFormatterTest {

    @Test
    fun `schema formatter removes leading plus from extended-year temporal values`() {
        val record =
            mapOf(
                "extended_date" to DateValue("+10000-01-02"),
                "extended_timestamp_without_timezone" to
                    TimestampWithoutTimezoneValue("+10000-01-02T03:04:05"),
                "extended_timestamp_with_timezone" to
                    TimestampWithTimezoneValue("+10000-01-02T03:04:05+07:00"),
                "normal_date" to DateValue("2025-01-02"),
                "negative_date" to DateValue("-0001-01-02"),
            )

        val formatted =
            PostgresSchemaRecordFormatter(
                    listOf(
                        "extended_date",
                        "extended_timestamp_without_timezone",
                        "extended_timestamp_with_timezone",
                        "normal_date",
                        "negative_date",
                    )
                )
                .format(record)

        assertEquals(
            listOf(
                "10000-01-02",
                "10000-01-02T03:04:05",
                "10000-01-02T03:04:05+07:00",
                "2025-01-02",
                "-0001-01-02",
            ),
            formatted,
        )
    }

    @Test
    fun `schema formatter removes nested null characters before serialization`() {
        val value =
            ObjectValue(
                linkedMapOf(
                    "entries" to
                        ArrayValue(
                            listOf(ObjectValue(linkedMapOf("text" to StringValue("a\u0000b"))))
                        )
                )
            )
        val enrichedValue =
            EnrichedAirbyteValue(
                abValue = value,
                type = ObjectTypeWithoutSchema,
                name = "entries",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val coercer = PostgresValueCoercer()
        coercer.map(enrichedValue)

        val serialized =
            PostgresSchemaRecordFormatter(listOf("entries"))
                .format(mapOf("entries" to enrichedValue.abValue))[0]
                .toString()

        assertFalse(serialized.contains('\u0000'))
        assertFalse(serialized.contains("\\u0000"))
    }

    @Test
    fun `raw formatter removes nested null characters before serialization`() {
        val value =
            ObjectValue(
                linkedMapOf(
                    "entries" to
                        ArrayValue(
                            listOf(ObjectValue(linkedMapOf("text" to StringValue("a\u0000b"))))
                        )
                )
            )
        val enrichedValue =
            EnrichedAirbyteValue(
                abValue = value,
                type = ObjectTypeWithoutSchema,
                name = "entries",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val coercer = PostgresValueCoercer()
        coercer.map(enrichedValue)

        val serialized =
            PostgresRawRecordFormatter(listOf("_airbyte_data"))
                .format(mapOf("entries" to enrichedValue.abValue))[0]
                .toString()

        assertFalse(serialized.contains('\u0000'))
        assertFalse(serialized.contains("\\u0000"))
    }
}
