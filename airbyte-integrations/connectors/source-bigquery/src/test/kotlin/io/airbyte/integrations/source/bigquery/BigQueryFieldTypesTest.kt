/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.sql.ResultSet
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock
import org.mockito.Mockito.never
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`

class BigQueryFieldTypesTest {

    private fun field(name: String, type: StandardSQLTypeName, vararg sub: Field): Field =
        Field.newBuilder(name, type, *sub).setMode(Field.Mode.NULLABLE).build()

    private fun repeated(name: String, type: StandardSQLTypeName, vararg sub: Field): Field =
        Field.newBuilder(name, type, *sub).setMode(Field.Mode.REPEATED).build()

    /** The driver's primitive getters throw on NULL; the getters must not call them. */
    @Test
    fun testNullSafeBooleanGetter() {
        val rs: ResultSet = mock(ResultSet::class.java)
        `when`(rs.getObject(1)).thenReturn(null)
        `when`(rs.getObject(2)).thenReturn(java.lang.Boolean.TRUE)
        `when`(rs.getObject(3)).thenReturn("false")
        `when`(rs.getObject(4)).thenReturn(1L)
        `when`(rs.wasNull()).thenReturn(false)
        Assertions.assertNull(NullSafeBooleanGetter.get(rs, 1))
        Assertions.assertEquals(true, NullSafeBooleanGetter.get(rs, 2))
        Assertions.assertEquals(false, NullSafeBooleanGetter.get(rs, 3))
        Assertions.assertEquals(true, NullSafeBooleanGetter.get(rs, 4))
        verify(rs, never()).getBoolean(1)
        Assertions.assertEquals(
            Jsons.booleanNode(true),
            BigQueryBooleanFieldType.jsonEncoder.encode(true)
        )
    }

    @Test
    fun testNullSafeLongGetter() {
        val rs: ResultSet = mock(ResultSet::class.java)
        `when`(rs.getObject(1)).thenReturn(null)
        `when`(rs.getObject(2)).thenReturn(42L)
        `when`(rs.getObject(3)).thenReturn(7)
        `when`(rs.getObject(4)).thenReturn("-9223372036854775808")
        `when`(rs.getObject(5)).thenReturn(BigDecimal("12"))
        `when`(rs.wasNull()).thenReturn(false)
        Assertions.assertNull(NullSafeLongGetter.get(rs, 1))
        Assertions.assertEquals(42L, NullSafeLongGetter.get(rs, 2))
        Assertions.assertEquals(7L, NullSafeLongGetter.get(rs, 3))
        Assertions.assertEquals(Long.MIN_VALUE, NullSafeLongGetter.get(rs, 4))
        Assertions.assertEquals(12L, NullSafeLongGetter.get(rs, 5))
        verify(rs, never()).getLong(1)
        Assertions.assertEquals(
            Jsons.numberNode(42L),
            BigQueryLongFieldType.jsonEncoder.encode(42L)
        )
        Assertions.assertEquals(
            42L,
            BigQueryLongFieldType.jsonDecoder.decode(Jsons.numberNode(42L))
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.INTEGER,
            BigQueryLongFieldType.airbyteSchemaType
        )
    }

    @Test
    fun testNullSafeDoubleGetter() {
        val rs: ResultSet = mock(ResultSet::class.java)
        `when`(rs.getObject(1)).thenReturn(null)
        `when`(rs.getObject(2)).thenReturn(0.25)
        `when`(rs.getObject(3)).thenReturn(3L)
        `when`(rs.getObject(4)).thenReturn("NaN")
        `when`(rs.getObject(5)).thenReturn(Double.NEGATIVE_INFINITY)
        `when`(rs.wasNull()).thenReturn(false)
        Assertions.assertNull(NullSafeDoubleGetter.get(rs, 1))
        Assertions.assertEquals(0.25, NullSafeDoubleGetter.get(rs, 2))
        Assertions.assertEquals(3.0, NullSafeDoubleGetter.get(rs, 3))
        Assertions.assertTrue(NullSafeDoubleGetter.get(rs, 4)!!.isNaN())
        Assertions.assertEquals(Double.NEGATIVE_INFINITY, NullSafeDoubleGetter.get(rs, 5))
        verify(rs, never()).getDouble(1)
        Assertions.assertEquals(
            Jsons.numberNode(0.25),
            BigQueryDoubleFieldType.jsonEncoder.encode(0.25)
        )
        Assertions.assertEquals(
            LeafAirbyteSchemaType.NUMBER,
            BigQueryDoubleFieldType.airbyteSchemaType
        )
    }

    @Test
    fun testScalarTypes() {
        val expected: Map<StandardSQLTypeName, FieldType> =
            mapOf(
                StandardSQLTypeName.BOOL to BigQueryBooleanFieldType,
                StandardSQLTypeName.INT64 to BigQueryLongFieldType,
                StandardSQLTypeName.FLOAT64 to BigQueryDoubleFieldType,
                StandardSQLTypeName.NUMERIC to BigDecimalFieldType,
                StandardSQLTypeName.BIGNUMERIC to BigQueryBigNumericFieldType,
                StandardSQLTypeName.STRING to StringFieldType,
                StandardSQLTypeName.BYTES to BytesFieldType,
                StandardSQLTypeName.DATE to BigQueryDateFieldType,
                StandardSQLTypeName.DATETIME to BigQueryDateTimeFieldType,
                StandardSQLTypeName.TIMESTAMP to OffsetDateTimeFieldType,
                StandardSQLTypeName.TIME to BigQueryTimeFieldType,
                StandardSQLTypeName.JSON to JsonStringFieldType,
                StandardSQLTypeName.GEOGRAPHY to StringFieldType,
                StandardSQLTypeName.INTERVAL to StringFieldType,
                StandardSQLTypeName.RANGE to StringFieldType,
            )
        for ((bqType, fieldType) in expected) {
            Assertions.assertEquals(
                fieldType,
                BigQueryFieldTypes.fromField(field("c", bqType)),
                bqType.name
            )
        }
    }

    @Test
    fun testTypeNamesFromJdbcMetadata() {
        Assertions.assertEquals(BigQueryLongFieldType, BigQueryFieldTypes.fromTypeName("INT64"))
        Assertions.assertEquals(BigQueryLongFieldType, BigQueryFieldTypes.fromTypeName("bigint"))
        Assertions.assertEquals(BigDecimalFieldType, BigQueryFieldTypes.fromTypeName("NUMERIC"))
        Assertions.assertEquals(
            BigQueryBigNumericFieldType,
            BigQueryFieldTypes.fromTypeName("BIGNUMERIC")
        )
        Assertions.assertEquals(
            OffsetDateTimeFieldType,
            BigQueryFieldTypes.fromTypeName("TIMESTAMP")
        )
        Assertions.assertEquals(
            BigQueryDateTimeFieldType,
            BigQueryFieldTypes.fromTypeName("DATETIME")
        )
        Assertions.assertEquals(
            BigQueryStructFieldType(null),
            BigQueryFieldTypes.fromTypeName("STRUCT")
        )
        Assertions.assertEquals(
            BigQueryArrayFieldType(PokemonFieldType),
            BigQueryFieldTypes.fromTypeName("ARRAY"),
        )
        Assertions.assertEquals(PokemonFieldType, BigQueryFieldTypes.fromTypeName("SOMETHING_NEW"))
        Assertions.assertEquals(PokemonFieldType, BigQueryFieldTypes.fromTypeName(null))
    }

    @Test
    fun testRepeatedScalar() {
        val type: FieldType =
            BigQueryFieldTypes.fromField(repeated("tags", StandardSQLTypeName.STRING))
        Assertions.assertEquals(BigQueryArrayFieldType(StringFieldType), type)
        Assertions.assertEquals(
            ArrayAirbyteSchemaType(LeafAirbyteSchemaType.STRING),
            type.airbyteSchemaType
        )
        Assertions.assertEquals(
            Jsons.readTree("""{"type":"array","items":{"type":"string"}}"""),
            BigQueryFieldTypes.jsonSchema(type),
        )
    }

    @Test
    fun testNestedStructAndRepeatedStruct() {
        val struct: Field =
            field(
                "s",
                StandardSQLTypeName.STRUCT,
                field("a", StandardSQLTypeName.STRING),
                field("n", StandardSQLTypeName.INT64),
                field("inner", StandardSQLTypeName.STRUCT, field("t", StandardSQLTypeName.TIME)),
                repeated(
                    "items",
                    StandardSQLTypeName.STRUCT,
                    field("f", StandardSQLTypeName.FLOAT64)
                ),
            )
        val type: FieldType = BigQueryFieldTypes.fromField(struct)
        Assertions.assertEquals(LeafAirbyteSchemaType.JSONB, type.airbyteSchemaType)
        Assertions.assertEquals(
            BigQueryStructFieldType(
                listOf(
                    EmittedField("a", StringFieldType),
                    EmittedField("n", BigQueryLongFieldType),
                    EmittedField(
                        "inner",
                        BigQueryStructFieldType(listOf(EmittedField("t", BigQueryTimeFieldType)))
                    ),
                    EmittedField(
                        "items",
                        BigQueryArrayFieldType(
                            BigQueryStructFieldType(
                                listOf(EmittedField("f", BigQueryDoubleFieldType))
                            )
                        ),
                    ),
                )
            ),
            type,
        )
        Assertions.assertEquals(
            Jsons.readTree(
                """
{"type":"object","properties":{
  "a":{"type":"string"},
  "n":{"type":"number","airbyte_type":"integer"},
  "inner":{"type":"object","properties":{"t":{"type":"string","format":"time","airbyte_type":"time_without_timezone"}}},
  "items":{"type":"array","items":{"type":"object","properties":{"f":{"type":"number"}}}}
}}
"""
            ),
            BigQueryFieldTypes.jsonSchema(type),
        )
        val repeatedStruct: FieldType =
            BigQueryFieldTypes.fromField(
                repeated("rs", StandardSQLTypeName.STRUCT, field("x", StandardSQLTypeName.BOOL))
            )
        Assertions.assertEquals(
            ArrayAirbyteSchemaType(LeafAirbyteSchemaType.JSONB),
            repeatedStruct.airbyteSchemaType,
        )
    }

    @Test
    fun testStructWithoutKnownFieldsRendersAPlainObject() {
        Assertions.assertEquals(
            Jsons.readTree("""{"type":"object"}"""),
            BigQueryFieldTypes.jsonSchema(BigQueryStructFieldType(null)),
        )
    }

    @Test
    fun testJsonSchemaIsAFreshCopy() {
        val a = BigQueryFieldTypes.jsonSchema(BigQueryLongFieldType)
        a.put("extra", true)
        Assertions.assertFalse(BigQueryFieldTypes.jsonSchema(BigQueryLongFieldType).has("extra"))
    }
}
