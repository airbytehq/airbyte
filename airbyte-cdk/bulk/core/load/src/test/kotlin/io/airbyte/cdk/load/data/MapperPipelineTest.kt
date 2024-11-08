/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import io.airbyte.cdk.load.test.util.ValueTestBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MapperPipelineTest {
    class TurnSchemalessObjectTypesIntoIntegers : AirbyteSchemaIdentityMapper {
        override fun mapObjectWithoutSchema(schema: ObjectTypeWithoutSchema): AirbyteType =
            IntegerType
    }

    class TurnSchemalessObjectsIntoIntegers : AirbyteValueIdentityMapper() {
        override fun mapObjectWithoutSchema(
            value: ObjectValue,
            schema: ObjectTypeWithoutSchema,
            path: List<String>
        ): AirbyteValue {
            if (value.values.size == 1) {
                throw IllegalStateException("Arbitrarily reject 1")
            }
            return IntegerValue(value.values.size.toLong())
        }
    }

    class TurnIntegerTypesIntoStrings : AirbyteSchemaIdentityMapper {
        override fun mapInteger(schema: IntegerType): AirbyteType = StringType
    }

    class TurnIntegersIntoStrings : AirbyteValueIdentityMapper() {
        override fun mapInteger(value: IntegerValue, path: List<String>): AirbyteValue {
            if (value.value == 2L) {
                throw IllegalStateException("Arbitrarily reject 2")
            }
            return StringValue(value.value.toString())
        }
    }

    private fun makePipeline(schema: AirbyteType) =
        MapperPipeline(
            schema,
            listOf(
                TurnIntegerTypesIntoStrings() to TurnIntegersIntoStrings(),
                TurnSchemalessObjectTypesIntoIntegers() to TurnSchemalessObjectsIntoIntegers(),
            )
        )

    @Test
    fun testSuccessfulPipeline() {
        val (inputSchema, expectedSchema) =
            SchemaRecordBuilder<Root>()
                .with(ObjectTypeWithoutSchema, IntegerType)
                .with(IntegerType, StringType)
                .withRecord()
                .with(IntegerType, StringType)
                .with(BooleanType, BooleanType) // expect unchanged
                .endRecord()
                .build()

        val pipeline = makePipeline(inputSchema)
        Assertions.assertEquals(
            expectedSchema,
            pipeline.finalSchema,
            "final schema matches expected transformed schema"
        )
    }

    @Test
    fun testRecordMapping() {
        val (inputValue, inputSchema, expectedOutput) =
            ValueTestBuilder<Root>()
                .with(
                    ObjectValue(linkedMapOf("a" to IntegerValue(1), "b" to IntegerValue(2))),
                    ObjectTypeWithoutSchema,
                    IntegerValue(2)
                )
                .with(IntegerValue(1), IntegerType, StringValue("1"))
                .withRecord()
                .with(IntegerValue(3), IntegerType, StringValue("3"))
                .with(BooleanValue(true), BooleanType, BooleanValue(true)) // expect unchanged
                .endRecord()
                .build()
        val pipeline = makePipeline(inputSchema)
        val (result, changes) = pipeline.map(inputValue)

        Assertions.assertEquals(0, changes.size, "no changes were captured")
        Assertions.assertEquals(expectedOutput, result, "data was transformed as expected")
    }

    @Test
    fun testFailedMapping() {
        val (inputValue, inputSchema, _) =
            ValueTestBuilder<Root>()
                .with(
                    ObjectValue(linkedMapOf("a" to IntegerValue(1))),
                    ObjectTypeWithoutSchema,
                    NullValue,
                    nullable = true
                ) // fail: reject size==1
                .with(IntegerValue(1), IntegerType, StringValue("1"))
                .withRecord()
                .with(IntegerValue(2), IntegerType, NullValue, nullable = true) // fail: reject 2
                .with(BooleanValue(true), BooleanType, BooleanValue(true)) // expect unchanged
                .endRecord()
                .build()
        val pipeline = makePipeline(inputSchema)
        val (_, changes) = pipeline.map(inputValue)

        Assertions.assertEquals(2, changes.size, "two failures were captured")
    }

    @Test
    fun testFailedMappingThrowsOnNonNullable() {
        val (inputValue, inputSchema, _) =
            ValueTestBuilder<Root>()
                .with(IntegerValue(2), IntegerType, NullValue, nullable = false) // fail: reject 2
                .build()

        val pipeline = makePipeline(inputSchema)

        Assertions.assertThrows(IllegalStateException::class.java) { pipeline.map(inputValue) }
    }
}
