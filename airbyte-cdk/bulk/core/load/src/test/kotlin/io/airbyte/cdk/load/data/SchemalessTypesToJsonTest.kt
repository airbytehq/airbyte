/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import io.airbyte.cdk.load.test.util.ValueTestBuilder
import io.airbyte.cdk.load.util.deserializeToNode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class SchemalessTypesToJsonTest {
    @Test
    fun testBasicTypeBehavior() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withRecord()
                .with(StringType)
                .with(IntegerType)
                .endRecord()
                .with(ObjectTypeWithoutSchema, StringType)
                .with(ObjectTypeWithEmptySchema, StringType)
                .with(ArrayTypeWithoutSchema, StringType)
                .with(ArrayType(FieldType(StringType, nullable = false)))
                .build()
        val mapper = SchemalessTypesToJson()
        val output = mapper.map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testNestedTypes() {
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .withRecord()
                .with(StringType)
                .with(ObjectTypeWithEmptySchema, StringType)
                .withRecord()
                .with(IntegerType)
                .with(ObjectTypeWithoutSchema, StringType)
                .endRecord()
                .with(
                    ArrayType(FieldType(ArrayTypeWithoutSchema, nullable = false)),
                    ArrayType(FieldType(StringType, nullable = false))
                )
                .endRecord()
                .build()
        val mapper = SchemalessTypesToJson()
        val output = mapper.map(inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    private val addressJson =
        """{"address":{"street":"123 Main St","city":"San Francisco","state":"CA"}}"""

    @Test
    fun testBasicValueBehavior() {
        val (inputValues, inputSchema, expectedOutput) =
            ValueTestBuilder<Root>()
                .withRecord()
                .with(StringValue("hello"), StringType)
                .with(IntegerValue(42), IntegerType)
                .endRecord()
                .with(
                    ObjectValue(linkedMapOf("foo" to StringValue("bar"))),
                    ObjectTypeWithoutSchema,
                    StringValue("""{"foo":"bar"}""")
                )
                .with(
                    addressJson.deserializeToNode().toAirbyteValue(ObjectTypeWithoutSchema),
                    ObjectTypeWithEmptySchema,
                    StringValue(addressJson)
                )
                .with(
                    ArrayValue(listOf(StringValue("hello"), StringValue("world"))),
                    ArrayTypeWithoutSchema,
                    StringValue("""["hello","world"]""")
                )
                .with(
                    ArrayValue(listOf(StringValue("hello"), StringValue("world"))),
                    ArrayType(FieldType(StringType, nullable = false))
                )
                .build()
        val mapper = SchemalessValuesToJson(DestinationRecord.Meta())
        val output = mapper.map(inputValues, inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }

    @Test
    fun testNestedBehavior() {
        val (inputValues, inputSchema, expectedOutput) =
            ValueTestBuilder<Root>()
                .withRecord()
                .with(StringValue("hello"), StringType)
                .with(
                    ObjectValue(linkedMapOf("foo" to StringValue("bar"))),
                    ObjectTypeWithEmptySchema,
                    StringValue("""{"foo":"bar"}""")
                )
                .withRecord()
                .with(IntegerValue(42), IntegerType)
                .with(
                    ObjectValue(linkedMapOf("foo" to StringValue("bar"))),
                    ObjectTypeWithoutSchema,
                    StringValue("""{"foo":"bar"}""")
                )
                .endRecord()
                .with(
                    ArrayValue(listOf(StringValue("hello"), StringValue("world"))),
                    ArrayTypeWithoutSchema,
                    StringValue("""["hello","world"]""")
                )
                .endRecord()
                .with(
                    ArrayValue(listOf(StringValue("hello"), StringValue("world"))),
                    ArrayType(FieldType(StringType, nullable = false))
                )
                .build()
        val mapper = SchemalessValuesToJson(DestinationRecord.Meta())
        val output = mapper.map(inputValues, inputSchema)
        Assertions.assertEquals(expectedOutput, output)
    }
}
