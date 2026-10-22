/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import io.airbyte.cdk.load.data.AirbyteValueCoercer
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.iceberg.parquet.IcebergObjectMode
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigDecimal
import java.math.BigInteger
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class IcebergUtilTest {
    private fun util(mode: IcebergObjectMode) =
        IcebergUtil(
            SimpleTableIdGenerator(),
            AirbyteValueCoercer(),
            IcebergSchemaOptions(mode),
        )

    private fun enriched(
        value: ObjectValue,
        type: ObjectType,
        name: String = "user",
    ) = EnrichedAirbyteValue(value, type, name, mutableListOf(), null)

    @Test
    fun `STRUCT mode recursively munges declared properties`() {
        val type =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                    "overflow" to FieldType(IntegerType, nullable = true),
                    "too_large" to FieldType(NumberType, nullable = true),
                    "union" to
                        FieldType(
                            UnionType(setOf(StringType, IntegerType), isLegacyUnion = false),
                            nullable = true,
                        ),
                    "schemaless" to FieldType(ObjectTypeWithoutSchema, nullable = true),
                    "items" to
                        FieldType(
                            ArrayType(
                                FieldType(
                                    ObjectType(
                                        linkedMapOf(
                                            "name" to FieldType(StringType, nullable = true),
                                            "active" to FieldType(BooleanType, nullable = true),
                                        ),
                                    ),
                                    nullable = true,
                                ),
                            ),
                            nullable = true,
                        ),
                ),
            )
        val value =
            enriched(
                ObjectValue(
                    linkedMapOf(
                        "id" to StringValue("not-an-integer"),
                        "overflow" to IntegerValue(BigInteger("9223372036854775808")),
                        "too_large" to NumberValue(BigDecimal("1E400")),
                        "union" to ObjectValue(linkedMapOf("value" to StringValue("union"))),
                        "schemaless" to ObjectValue(linkedMapOf("value" to StringValue("json"))),
                        "items" to
                            ArrayValue(
                                listOf(
                                    ObjectValue(
                                        linkedMapOf(
                                            "name" to StringValue("first"),
                                            "active" to StringValue("not-a-boolean"),
                                            "extra" to StringValue("drop"),
                                        ),
                                    ),
                                    ObjectValue(
                                        linkedMapOf(
                                            "name" to StringValue("second"),
                                            "active" to BooleanValue(true),
                                            "extra" to StringValue("drop"),
                                        ),
                                    ),
                                ),
                            ),
                        "undeclared" to StringValue("drop"),
                    ),
                ),
                type,
            )

        util(IcebergObjectMode.STRUCT).mungeForIceberg(value)
        val result = value.abValue as ObjectValue
        val items = (result.values["items"] as ArrayValue).values

        assertThat(result.values.keys)
            .containsExactly("id", "overflow", "too_large", "union", "schemaless", "items")
        assertThat(result.values["id"]).isEqualTo(NullValue)
        assertThat(result.values["overflow"]).isEqualTo(NullValue)
        assertThat(result.values["too_large"]).isEqualTo(NullValue)
        assertThat(result.values["union"]).isEqualTo(StringValue("""{"value":"union"}"""))
        assertThat(result.values["schemaless"]).isEqualTo(StringValue("""{"value":"json"}"""))
        assertThat((items[0] as ObjectValue).values.keys).containsExactly("name", "active")
        assertThat((items[0] as ObjectValue).values["active"]).isEqualTo(NullValue)
        assertThat((items[1] as ObjectValue).values["active"]).isEqualTo(BooleanValue(true))
        assertThat(value.changes)
            .containsExactly(
                Meta.Change("user.id", Change.NULLED, Reason.DESTINATION_SERIALIZATION_ERROR),
                Meta.Change(
                    "user.overflow",
                    Change.NULLED,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                ),
                Meta.Change(
                    "user.too_large",
                    Change.NULLED,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                ),
                Meta.Change(
                    "user.items.0.active",
                    Change.NULLED,
                    Reason.DESTINATION_SERIALIZATION_ERROR,
                ),
            )
    }

    @Test
    fun `JSON_STRING mode keeps the existing object serialization path`() {
        val type =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = false),
                ),
            )
        val value =
            enriched(
                ObjectValue(linkedMapOf("id" to IntegerValue(42L))),
                type,
            )

        util(IcebergObjectMode.JSON_STRING).mungeForIceberg(value)

        assertThat(value.abValue).isEqualTo(StringValue("""{"id":42}"""))
        assertThat(value.changes).isEmpty()
    }
}
