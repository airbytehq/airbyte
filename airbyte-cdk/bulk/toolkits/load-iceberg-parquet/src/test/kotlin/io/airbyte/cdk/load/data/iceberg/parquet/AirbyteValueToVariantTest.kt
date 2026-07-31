/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import java.math.BigDecimal
import java.math.BigInteger
import org.apache.iceberg.variants.PhysicalType
import org.apache.iceberg.variants.VariantArray
import org.apache.iceberg.variants.VariantObject
import org.apache.iceberg.variants.VariantPrimitive
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class AirbyteValueToVariantTest {

    private val converter = AirbyteValueToVariant()

    @Test
    fun `converts objects while preserving value types`() {
        val value =
            ObjectValue(
                linkedMapOf(
                    "name" to StringValue("airbyte"),
                    "count" to IntegerValue(42),
                    "ratio" to NumberValue(BigDecimal("1.50")),
                    "enabled" to BooleanValue(true),
                    "missing" to NullValue,
                ),
            )

        val obj = converter.convert(value).value() as VariantObject

        assertEquals(PhysicalType.STRING, (obj.get("name") as VariantPrimitive<*>).type())
        assertEquals("airbyte", (obj.get("name") as VariantPrimitive<*>).get())
        assertEquals(PhysicalType.INT64, (obj.get("count") as VariantPrimitive<*>).type())
        assertEquals(42L, (obj.get("count") as VariantPrimitive<*>).get())
        assertEquals(BigDecimal("1.50"), (obj.get("ratio") as VariantPrimitive<*>).get())
        assertEquals(true, (obj.get("enabled") as VariantPrimitive<*>).get())
        assertEquals(PhysicalType.NULL, (obj.get("missing") as VariantPrimitive<*>).type())
    }

    @Test
    fun `converts nested objects and arrays`() {
        val value =
            ObjectValue(
                linkedMapOf(
                    "items" to
                        ArrayValue(
                            listOf(
                                IntegerValue(1),
                                ObjectValue(linkedMapOf("deep" to StringValue("value"))),
                            ),
                        ),
                ),
            )

        val obj = converter.convert(value).value() as VariantObject
        val array = obj.get("items") as VariantArray

        assertEquals(2, array.numElements())
        assertEquals(1L, (array.get(0) as VariantPrimitive<*>).get())
        val nested = array.get(1) as VariantObject
        assertEquals("value", (nested.get("deep") as VariantPrimitive<*>).get())
    }

    @Test
    fun `converts temporal values to variant temporal types`() {
        val value =
            ObjectValue(
                linkedMapOf(
                    "date" to DateValue("2026-01-02"),
                    "tstz" to TimestampWithTimezoneValue("2026-01-02T03:04:05Z"),
                    "tsntz" to TimestampWithoutTimezoneValue("2026-01-02T03:04:05"),
                ),
            )

        val obj = converter.convert(value).value() as VariantObject

        assertEquals(PhysicalType.DATE, (obj.get("date") as VariantPrimitive<*>).type())
        assertEquals(
            PhysicalType.TIMESTAMPTZ,
            (obj.get("tstz") as VariantPrimitive<*>).type(),
        )
        assertEquals(
            PhysicalType.TIMESTAMPNTZ,
            (obj.get("tsntz") as VariantPrimitive<*>).type(),
        )
    }

    @Test
    fun `converts integers wider than int64 to decimal`() {
        val wide = BigInteger("123456789012345678901234567890")
        val value = ObjectValue(linkedMapOf("big" to IntegerValue(wide)))

        val obj = converter.convert(value).value() as VariantObject

        assertEquals(PhysicalType.DECIMAL16, (obj.get("big") as VariantPrimitive<*>).type())
        assertEquals(wide.toBigDecimal(), (obj.get("big") as VariantPrimitive<*>).get())
    }

    @Test
    fun `converts top level scalars`() {
        val primitive = converter.convert(StringValue("scalar")).value() as VariantPrimitive<*>

        assertEquals("scalar", primitive.get())
    }
}
