/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import io.airbyte.cdk.load.test.util.ValueTestBuilder
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
}
