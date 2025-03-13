/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineTest
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Test

class ParquetMapperBatchPipelineTest {
    @Test
    fun `test conversions nested in unions`() {
        val stream = mockk<DestinationStream>()
        val schema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(StringType, true),
                    "plan" to
                        FieldType(
                            UnionType(
                                setOf(
                                    ObjectType(
                                        linkedMapOf(
                                            "id" to FieldType(StringType, true),
                                            "price" to FieldType(NumberType, true),
                                            "tiers" to
                                                FieldType(
                                                    UnionType(
                                                        setOf(
                                                            ObjectType(
                                                                linkedMapOf(
                                                                    "up_to" to
                                                                        FieldType(
                                                                            IntegerType,
                                                                            true
                                                                        ),
                                                                    "name" to
                                                                        FieldType(StringType, true),
                                                                )
                                                            ),
                                                            StringType
                                                        )
                                                    ),
                                                    true
                                                ),
                                            "metadata" to FieldType(ObjectTypeWithEmptySchema, true)
                                        )
                                    ),
                                    StringType
                                )
                            ),
                            true
                        )
                )
            )
        every { stream.schema } returns schema
        every { stream.syncId } returns 101L
        every { stream.generationId } returns 202L

        val record =
            ObjectValue(
                linkedMapOf(
                    "id" to StringValue("1"),
                    "plan" to
                        ObjectValue(
                            linkedMapOf(
                                "id" to StringValue("2"),
                                "price" to NumberValue(10.0.toBigDecimal()),
                                "tiers" to
                                    ObjectValue(
                                        linkedMapOf(
                                            "up_to" to IntegerValue(10),
                                            "name" to StringValue("tier1")
                                        )
                                    ),
                                "metadata" to
                                    ObjectValue(linkedMapOf("key" to StringValue("value")))
                            )
                        ),
                )
            )
        val pipeline = ParquetMapperPipelineTest().create(stream)
        val schemaMapped = pipeline.finalSchema as ObjectType
        val (recordMapped, _) = pipeline.map(record)

        val planSchema = schemaMapped.properties["plan"]?.type as ObjectType
        val planObjectOption = planSchema.properties["object"]?.type as ObjectType
        assert(planObjectOption.properties["tiers"]?.type is ObjectType) {
            "Unions nested within converted unions should also be converted"
        }

        val planValue = (recordMapped as ObjectValue).values["plan"] as ObjectValue
        val planObjectValue = planValue.values["object"] as ObjectValue
        assert(planObjectValue.values["metadata"] is StringValue) {
            "Schemaless types values nested within converted unions should be converted"
        }
    }
}
