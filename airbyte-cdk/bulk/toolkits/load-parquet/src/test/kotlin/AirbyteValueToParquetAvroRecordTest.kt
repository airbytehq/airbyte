/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.avro.toAvroRecord
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.parquet.ParquetMapperPipelineFactory
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteValueToParquetAvroRecordTest {
    @Test
    fun `test schemaless types`() {
        val stream = mockk<DestinationStream>()
        every { stream.descriptor } returns DestinationStream.Descriptor("test", "stream")
        every { stream.syncId } returns 100L
        every { stream.generationId } returns 200L

        val schema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(StringType, true),
                    "plan" to
                        FieldType(
                            ObjectType(
                                linkedMapOf(
                                    "plan_id" to FieldType(StringType, true),
                                    "array_of_unions" to
                                        FieldType(
                                            ArrayType(
                                                items =
                                                    FieldType(
                                                        UnionType.of(
                                                            StringType,
                                                            ObjectType(
                                                                linkedMapOf(
                                                                    "name" to
                                                                        FieldType(StringType, true)
                                                                )
                                                            )
                                                        ),
                                                        true
                                                    )
                                            ),
                                            true
                                        ),
                                    "field1" to FieldType(IntegerType, true),
                                    "field2" to FieldType(IntegerType, true),
                                    "field3" to FieldType(IntegerType, true),
                                    "field4" to FieldType(IntegerType, true),
                                    "field5" to FieldType(IntegerType, true),
                                    "field6" to FieldType(IntegerType, true),
                                    "field7" to FieldType(IntegerType, true),
                                    "field8" to FieldType(IntegerType, true),
                                    "field9" to FieldType(IntegerType, true),
                                    "field10" to FieldType(IntegerType, true),
                                    "object" to
                                        FieldType(
                                            ObjectType(
                                                linkedMapOf(
                                                    "object_id" to FieldType(StringType, true),
                                                    "metadata" to
                                                        FieldType(ObjectTypeWithEmptySchema, true)
                                                )
                                            ),
                                            true
                                        ),
                                )
                            ),
                            true
                        )
                )
            )

        every { stream.schema } returns schema

        val record =
            ObjectValue(
                linkedMapOf(
                    "id" to StringValue("123"),
                    "plan" to
                        ObjectValue(
                            linkedMapOf(
                                "plan_id" to StringValue("456"),
                                "array_of_unions" to
                                    ArrayValue(
                                        listOf(
                                            StringValue("abc"),
                                            ObjectValue(linkedMapOf("name" to StringValue("def")))
                                        )
                                    ),
                                "field1" to IntegerValue(1),
                                "field2" to IntegerValue(2),
                                "field3" to IntegerValue(3),
                                "field4" to IntegerValue(4),
                                "field5" to IntegerValue(5),
                                "field6" to IntegerValue(6),
                                "field7" to IntegerValue(7),
                                "field8" to IntegerValue(8),
                                "field9" to IntegerValue(9),
                                "object" to
                                    ObjectValue(
                                        linkedMapOf(
                                            "object_id" to StringValue("789"),
                                            "metadata" to
                                                ObjectValue(
                                                    linkedMapOf(
                                                        "schemaless_id" to StringValue("789")
                                                    )
                                                )
                                        )
                                    )
                            )
                        )
                )
            )

        val pipeline = ParquetMapperPipelineFactory().create(stream)
        val recordMapped = pipeline.map(record).withAirbyteMeta(stream, 0, flatten = true)
        val schemaWithMeta = pipeline.finalSchema.withAirbyteMeta(true)
        val avroSchema = schemaWithMeta.toAvroSchema(stream.descriptor)
        val avroRecord = recordMapped.toAvroRecord(schemaWithMeta, avroSchema)
        println(avroRecord.toString())

        Assertions.assertEquals(
            """{"nested_id": "456", "schemaless": "{\"schemaless_id\":\"789\"}"}""",
            avroRecord.toString()
        )
    }
}
