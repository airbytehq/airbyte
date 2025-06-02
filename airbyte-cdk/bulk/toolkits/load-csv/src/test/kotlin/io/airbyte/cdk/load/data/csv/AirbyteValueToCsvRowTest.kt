/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.math.BigInteger
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class AirbyteValueToCsvRowTest {

    @Test
    fun `toCsvRecord processes values using provided processor`() {
        val processor = mockk<CsvValueProcessor>()

        // Setup mock responses
        every { processor.process(StringValue("test")) } returns "processed_string"
        every { processor.process(IntegerValue(42)) } returns "processed_int"
        every { processor.process(null) } returns "processed_null"

        val schema =
            ObjectType(
                properties =
                    linkedMapOf(
                        "field1" to FieldType(StringType, false),
                        "field2" to FieldType(IntegerType, false),
                        "field3" to FieldType(StringType, true)
                    )
            )

        val objectValue =
            ObjectValue(
                values =
                    linkedMapOf(
                        "field1" to StringValue("test"),
                        "field2" to IntegerValue(42)
                        // field3 is missing (null)
                        )
            )

        val result = objectValue.toCsvRecord(schema, processor)

        assertEquals(3, result.size)
        assertEquals(listOf("processed_string", "processed_int", "processed_null"), result)

        // Verify processor was called for each field
        verify { processor.process(StringValue("test")) }
        verify { processor.process(IntegerValue(42)) }
        verify { processor.process(null) }
    }

    @Test
    fun `toCsvRecord maintains field order according to schema`() {
        val processor = DefaultCsvValueProcessor()

        val schema =
            ObjectType(
                properties =
                    linkedMapOf(
                        "z_field" to FieldType(StringType, false),
                        "a_field" to FieldType(StringType, false),
                        "m_field" to FieldType(StringType, false)
                    )
            )

        val objectValue =
            ObjectValue(
                values =
                    linkedMapOf(
                        "a_field" to StringValue("a_value"),
                        "z_field" to StringValue("z_value"),
                        "m_field" to StringValue("m_value")
                    )
            )

        val result = objectValue.toCsvRecord(schema, processor)

        assertEquals(3, result.size)
        // Order should match schema property order, not alphabetical
        assertEquals(listOf("z_value", "a_value", "m_value"), result)
    }

    @Test
    fun `toCsvRecord handles empty object with schema`() {
        val processor = DefaultCsvValueProcessor()

        val schema =
            ObjectType(
                properties =
                    linkedMapOf(
                        "field1" to FieldType(StringType, true),
                        "field2" to FieldType(IntegerType, true)
                    )
            )

        val objectValue = ObjectValue(values = linkedMapOf())

        val result = objectValue.toCsvRecord(schema, processor)

        assertEquals(2, result.size)
        assertEquals(listOf("", ""), result)
    }

    @Test
    fun `toCsvRecord with custom processor behavior`() {
        val customProcessor =
            object : CsvValueProcessor {
                override fun process(value: AirbyteValue?): Any {
                    return when (value) {
                        is StringValue -> value.value.uppercase()
                        is IntegerValue -> value.value * BigInteger.valueOf(10)
                        null -> "MISSING"
                        else -> value.toString()
                    }
                }
            }

        val schema =
            ObjectType(
                properties =
                    linkedMapOf(
                        "name" to FieldType(StringType, false),
                        "count" to FieldType(IntegerType, false),
                        "missing" to FieldType(StringType, true)
                    )
            )

        val objectValue =
            ObjectValue(
                values =
                    linkedMapOf(
                        "name" to StringValue("hello"),
                        "count" to IntegerValue(5)
                        // missing field intentionally omitted
                        )
            )

        val result = objectValue.toCsvRecord(schema, customProcessor)

        assertEquals(3, result.size)
        assertEquals(listOf("HELLO", BigInteger.valueOf(50), "MISSING"), result)
    }
}
