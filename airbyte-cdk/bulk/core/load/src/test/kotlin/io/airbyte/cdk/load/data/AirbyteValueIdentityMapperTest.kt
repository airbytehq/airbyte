/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import io.airbyte.cdk.load.test.util.ValueTestBuilder
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteValueIdentityMapperTest {
    @Test
    fun testIdentityMapping() {
        val (inputValues, inputSchema, expectedValues) =
            ValueTestBuilder<SchemaRecordBuilder<Root>>()
                .with(StringValue("a"), StringType)
                .with(IntegerValue(1), IntegerType)
                .with(BooleanValue(true), BooleanType)
                .with(TimestampValue("2021-01-01T12:00:00Z"), TimestampTypeWithTimezone)
                .with(TimestampValue("2021-01-01T12:00:00"), TimestampTypeWithoutTimezone)
                .with(TimeValue("12:00:00Z"), TimeTypeWithTimezone)
                .with(TimeValue("12:00:00"), TimeTypeWithoutTimezone)
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
                .with(NullValue, NullType)
                .endRecord()
                .endRecord()
                .build()

        val meta = DestinationRecord.Meta()
        val values = AirbyteValueIdentityMapper(meta).map(inputValues, inputSchema)
        Assertions.assertEquals(expectedValues, values)
        Assertions.assertTrue(meta.changes.isEmpty())
    }

    @Test
    fun testIdentityMappingWithBadSchema() {
        val (inputValues, inputSchema, _) =
            ValueTestBuilder<SchemaRecordBuilder<Root>>()
                .with(StringValue("a"), StringType)
                .with(
                    TimestampValue("2021-01-01T12:00:00Z"),
                    TimeTypeWithTimezone,
                    nameOverride = "bad"
                )
                .build()
        val meta = DestinationRecord.Meta()
        val values = AirbyteValueIdentityMapper(meta).map(inputValues, inputSchema) as ObjectValue
        Assertions.assertTrue(meta.changes.isNotEmpty())
        Assertions.assertTrue(values.values["bad"] is NullValue)
        Assertions.assertTrue(meta.changes[0].field == "bad")
        Assertions.assertTrue(
            meta.changes[0].change == AirbyteRecordMessageMetaChange.Change.NULLED
        )
        Assertions.assertTrue(
            meta.changes[0].reason ==
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_SERIALIZATION_ERROR
        )
    }
}
