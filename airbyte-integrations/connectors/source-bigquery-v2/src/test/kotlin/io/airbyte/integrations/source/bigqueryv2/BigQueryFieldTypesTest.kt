/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.google.cloud.bigquery.Field
import com.google.cloud.bigquery.StandardSQLTypeName
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BigQueryFieldTypesTest {

    private fun field(name: String, type: StandardSQLTypeName, vararg sub: Field): Field =
        Field.newBuilder(name, type, *sub).setMode(Field.Mode.NULLABLE).build()

    private fun repeated(name: String, type: StandardSQLTypeName, vararg sub: Field): Field =
        Field.newBuilder(name, type, *sub).setMode(Field.Mode.REPEATED).build()

    @Test
    fun testScalarTypes() {
        val expected: Map<StandardSQLTypeName, FieldType> =
            mapOf(
                StandardSQLTypeName.BOOL to BooleanFieldType,
                StandardSQLTypeName.INT64 to LongFieldType,
                StandardSQLTypeName.FLOAT64 to DoubleFieldType,
                StandardSQLTypeName.NUMERIC to BigDecimalFieldType,
                StandardSQLTypeName.BIGNUMERIC to BigDecimalFieldType,
                StandardSQLTypeName.STRING to StringFieldType,
                StandardSQLTypeName.BYTES to BytesFieldType,
                StandardSQLTypeName.DATE to LocalDateFieldType,
                StandardSQLTypeName.DATETIME to LocalDateTimeFieldType,
                StandardSQLTypeName.TIMESTAMP to OffsetDateTimeFieldType,
                StandardSQLTypeName.TIME to LocalTimeFieldType,
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
        Assertions.assertEquals(LongFieldType, BigQueryFieldTypes.fromTypeName("INT64"))
        Assertions.assertEquals(LongFieldType, BigQueryFieldTypes.fromTypeName("bigint"))
        Assertions.assertEquals(BigDecimalFieldType, BigQueryFieldTypes.fromTypeName("BIGNUMERIC"))
        Assertions.assertEquals(
            OffsetDateTimeFieldType,
            BigQueryFieldTypes.fromTypeName("TIMESTAMP")
        )
        Assertions.assertEquals(LocalDateTimeFieldType, BigQueryFieldTypes.fromTypeName("DATETIME"))
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
                    EmittedField("n", LongFieldType),
                    EmittedField(
                        "inner",
                        BigQueryStructFieldType(listOf(EmittedField("t", LocalTimeFieldType)))
                    ),
                    EmittedField(
                        "items",
                        BigQueryArrayFieldType(
                            BigQueryStructFieldType(listOf(EmittedField("f", DoubleFieldType)))
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
        val a = BigQueryFieldTypes.jsonSchema(LongFieldType)
        a.put("extra", true)
        Assertions.assertFalse(BigQueryFieldTypes.jsonSchema(LongFieldType).has("extra"))
    }
}
