/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import io.airbyte.cdk.load.test.util.ValueTestBuilder
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

class AirbyteValueIdentityMapperTest {
    @Test
    fun testIdentityMapping() {
        val (inputValues, inputSchema, expectedValues) =
            ValueTestBuilder<SchemaRecordBuilder<Root>>()
                .with(StringValue("a"), StringType)
                .with(IntegerValue(1), IntegerType)
                .with(BooleanValue(true), BooleanType)
                .with(TimestampWithTimezoneValue("2021-01-01T12:00:00Z"), TimestampTypeWithTimezone)
                .with(
                    TimestampWithoutTimezoneValue("2021-01-01T12:00:00"),
                    TimestampTypeWithoutTimezone
                )
                .with(TimeWithTimezoneValue("12:00:00Z"), TimeTypeWithTimezone)
                .with(TimeWithoutTimezoneValue("12:00:00"), TimeTypeWithoutTimezone)
                .with(DateValue("2021-01-01"), DateType)
                .withRecord()
                .with(
                    ArrayValue(listOf("a", "b", "c").map(::StringValue)),
                    ArrayType(FieldType(StringType, false))
                )
                .with(
                    ArrayValue(listOf(IntegerValue(1), BooleanValue(true))),
                    ArrayTypeWithoutSchema
                )
                .withRecord()
                .endRecord()
                .endRecord()
                .build()

        val mapper = AirbyteValueIdentityMapper()
        val (values, changes) = mapper.map(inputValues, inputSchema)
        Assertions.assertEquals(expectedValues, values)
        Assertions.assertTrue(changes.isEmpty())
    }

    @Test
    fun testIdentityMappingWithBadSchema() {
        val (inputValues, inputSchema, _) =
            ValueTestBuilder<SchemaRecordBuilder<Root>>()
                .with(StringValue("a"), StringType)
                .with(IntegerValue(1000), BooleanType, nameOverride = "bad", nullable = true)
                .build()
        val mapper = AirbyteValueIdentityMapper()
        val (values, changes) = mapper.map(inputValues, inputSchema)
        assertAll(
            { Assertions.assertEquals(emptyList<Meta.Change>(), changes) },
            { Assertions.assertEquals(IntegerValue(1000), (values as ObjectValue).values["bad"]) },
        )
    }

    @Test
    fun testNonRecursiveMapping() {
        val type =
            ObjectType(
                linkedMapOf(
                    "int" to f(IntegerType),
                    "object" to
                        f(
                            ObjectType(
                                linkedMapOf("sub_int" to FieldType(IntegerType, nullable = true))
                            ),
                        ),
                    "array" to f(ArrayType(f(IntegerType))),
                    "union" to f(UnionType(setOf(IntegerType, BooleanType))),
                )
            )
        val value =
            ObjectValue(
                linkedMapOf(
                    "int" to StringValue("invalid1"),
                    "object" to ObjectValue(linkedMapOf("sub_int" to StringValue("invalid2"))),
                    "array" to ArrayValue(listOf(StringValue("invalid3"))),
                    "union" to IntegerValue(42),
                )
            )

        // Dumb mapper, which nulls all root-level integer fields
        val mapper =
            object :
                AirbyteValueIdentityMapper(
                    recurseIntoObjects = false,
                    recurseIntoArrays = false,
                    recurseIntoUnions = false,
                ) {
                override fun mapInteger(
                    value: AirbyteValue,
                    context: Context
                ): Pair<AirbyteValue, Context> = nulledOut(IntegerType, context)
            }

        val (mappedValue, changes) = mapper.map(value, type)
        assertAll(
            {
                assertEquals(
                    ObjectValue(
                        linkedMapOf(
                            // The root int was nulled
                            "int" to NullValue,
                            // The nested ints were not nulled
                            "object" to
                                ObjectValue(linkedMapOf("sub_int" to StringValue("invalid2"))),
                            "array" to ArrayValue(listOf(StringValue("invalid3"))),
                            "union" to IntegerValue(42),
                        )
                    ),
                    mappedValue
                )
            },
            {
                assertEquals(
                    listOf(
                        Meta.Change("int", Change.NULLED, Reason.DESTINATION_SERIALIZATION_ERROR),
                    ),
                    changes
                )
            }
        )
    }

    private fun f(type: AirbyteType) = FieldType(type, nullable = true)
}
