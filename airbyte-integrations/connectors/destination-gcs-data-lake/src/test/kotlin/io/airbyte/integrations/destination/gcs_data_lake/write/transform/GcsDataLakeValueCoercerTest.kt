/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write.transform

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.iceberg.parquet.AirbyteValueToIcebergRecord
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.mockk.mockk
import java.math.BigDecimal
import java.math.BigInteger
import org.apache.iceberg.types.Type
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class GcsDataLakeValueCoercerTest {
    private val coercer =
        GcsDataLakeValueCoercer(
            IcebergUtil(mockk<TableIdGenerator>(relaxed = true), AirbyteValueCoercer()),
        )
    private val converter = AirbyteValueToIcebergRecord()

    @Test
    fun `stringifies object elements in arrays`() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "dt" to FieldType(IntegerType, nullable = true),
                    "main" to
                        FieldType(
                            ObjectType(
                                linkedMapOf("aqi" to FieldType(IntegerType, nullable = true)),
                            ),
                            nullable = true,
                        ),
                    "components" to
                        FieldType(
                            ObjectType(linkedMapOf("co" to FieldType(NumberType, nullable = true))),
                            nullable = true,
                        ),
                ),
            )
        val objectValue =
            ObjectValue(
                linkedMapOf(
                    "dt" to IntegerValue(1L),
                    "main" to ObjectValue(linkedMapOf("aqi" to IntegerValue(2L))),
                    "components" to
                        ObjectValue(linkedMapOf("co" to NumberValue(BigDecimal("1.5")))),
                ),
            )

        val (result, converted) =
            mapAndConvert(
                ArrayType(FieldType(objectType, nullable = true)),
                ArrayValue(listOf(objectValue)),
            )

        assertEquals(
            ArrayValue(listOf(StringValue(objectValue.serializeToString()))),
            result.abValue,
        )
        assertEquals(listOf(objectValue.serializeToString()), converted)
    }

    @Test
    fun `stringifies objects in nested arrays`() {
        val objectType = ObjectType(linkedMapOf("id" to FieldType(IntegerType, nullable = true)))
        val firstObject = ObjectValue(linkedMapOf("id" to IntegerValue(1L)))
        val secondObject = ObjectValue(linkedMapOf("id" to IntegerValue(2L)))
        val type =
            ArrayType(
                FieldType(
                    ArrayType(FieldType(objectType, nullable = true)),
                    nullable = true,
                ),
            )
        val value = ArrayValue(listOf(ArrayValue(listOf(firstObject, secondObject))))

        val (result, converted) = mapAndConvert(type, value)

        assertEquals(
            ArrayValue(
                listOf(
                    ArrayValue(
                        listOf(
                            StringValue(firstObject.serializeToString()),
                            StringValue(secondObject.serializeToString()),
                        ),
                    ),
                ),
            ),
            result.abValue,
        )
        assertEquals(
            listOf(listOf(firstObject.serializeToString(), secondObject.serializeToString())),
            converted,
        )
    }

    @Test
    fun `stringifies nontrivial union elements in arrays`() {
        val objectType = ObjectType(linkedMapOf("id" to FieldType(IntegerType, nullable = true)))
        val unionType = UnionType(setOf(objectType, StringType), isLegacyUnion = false)
        val objectValue = ObjectValue(linkedMapOf("id" to IntegerValue(42L)))

        val (result, converted) =
            mapAndConvert(
                ArrayType(FieldType(unionType, nullable = true)),
                ArrayValue(listOf(objectValue)),
            )

        assertEquals(
            ArrayValue(listOf(StringValue(objectValue.serializeToString()))),
            result.abValue,
        )
        assertEquals(listOf(objectValue.serializeToString()), converted)
    }

    @Test
    fun `leaves integer elements in arrays unchanged`() {
        val type = ArrayType(FieldType(IntegerType, nullable = true))
        val value = ArrayValue(listOf(IntegerValue(1L), IntegerValue(2L)))

        val (result, converted) = mapAndConvert(type, value)

        assertEquals(value, result.abValue)
        assertEquals(listOf(1L, 2L), converted)
    }

    @Test
    fun `stringifies top level unions but preserves null values`() {
        val unionType = UnionType(setOf(StringType, IntegerType), isLegacyUnion = false)
        val unionValue = IntegerValue(42L)
        val (result, converted) = mapAndConvert(unionType, unionValue)

        assertEquals(StringValue(unionValue.serializeToString()), result.abValue)
        assertEquals(unionValue.serializeToString(), converted)

        val (nullResult, nullConverted) = mapAndConvert(unionType, NullValue)

        assertEquals(NullValue, nullResult.abValue)
        assertEquals(null, nullConverted)
    }

    @Test
    fun `preserves null elements in arrays of objects`() {
        val objectType = ObjectType(linkedMapOf("id" to FieldType(IntegerType, nullable = true)))
        val objectValue = ObjectValue(linkedMapOf("id" to IntegerValue(1L)))
        val type = ArrayType(FieldType(objectType, nullable = true))

        val (result, converted) = mapAndConvert(type, ArrayValue(listOf(objectValue, NullValue)))

        assertEquals(
            ArrayValue(listOf(StringValue(objectValue.serializeToString()), NullValue)),
            result.abValue,
        )
        assertEquals(listOf(objectValue.serializeToString(), null), converted)
    }

    @Test
    fun `passes through scalar values with unknown types`() {
        val unknownType = UnknownType(Jsons.readTree("""{"type":"potato"}"""))
        val value = StringValue("ex falso quodlibet")

        val result = coercer.map(enriched(value, unknownType))

        assertEquals(value, result.abValue)
    }

    @Test
    fun `stringifies object elements in arrays with unknown item types`() {
        val unknownType = UnknownType(Jsons.readTree("""{"type":"potato"}"""))
        val objectValue = ObjectValue(linkedMapOf("id" to IntegerValue(1L)))

        val (result, converted) =
            mapAndConvert(
                ArrayType(FieldType(unknownType, nullable = true)),
                ArrayValue(listOf(objectValue)),
            )

        assertEquals(
            ArrayValue(listOf(StringValue(objectValue.serializeToString()))),
            result.abValue,
        )
        assertEquals(listOf(objectValue.serializeToString()), converted)
    }

    @Test
    fun `validates integer and number destination limits`() {
        val integerType = IntegerType
        val outOfRangeInteger = IntegerValue(BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE))
        val inRangeInteger = IntegerValue(Long.MAX_VALUE)
        val outOfRangeNumber = NumberValue(BigDecimal("1e309"))

        assertEquals(
            ValidationResult.ShouldNullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION),
            coercer.validate(enriched(outOfRangeInteger, integerType)),
        )
        assertEquals(
            ValidationResult.Valid,
            coercer.validate(enriched(inRangeInteger, integerType)),
        )
        assertEquals(
            ValidationResult.ShouldNullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION),
            coercer.validate(enriched(outOfRangeNumber, NumberType)),
        )
    }

    private fun mapAndConvert(
        type: AirbyteType,
        value: AirbyteValue,
    ): Pair<EnrichedAirbyteValue, Any?> {
        val icebergType = icebergType(type)
        val result = coercer.map(enriched(value, type))
        return result to converter.convert(result.abValue, icebergType)
    }

    private fun enriched(
        value: AirbyteValue,
        type: AirbyteType,
    ) = EnrichedAirbyteValue(abValue = value, type = type, name = "col", airbyteMetaField = null)

    private fun icebergType(type: AirbyteType): Type =
        ObjectType(linkedMapOf("col" to FieldType(type, nullable = true)))
            .toIcebergSchema(emptyList())
            .findField("col")
            .type()
}
