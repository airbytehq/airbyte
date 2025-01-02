/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.avro.AvroMapperPipelineFactory
import io.airbyte.cdk.load.data.avro.toAvroRecord
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.mockk.every
import io.mockk.mockk
import org.junit.Assert.assertEquals
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteValueToAvroRecordTest {

    @Test
    fun `test arrays of unions`() {
        val stream = mockk<DestinationStream>()
        every { stream.descriptor } returns DestinationStream.Descriptor("test", "stream")

        val schema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(StringType, true),
                    "array_of_unions" to
                        FieldType(
                            ArrayType(
                                items =
                                    FieldType(
                                        UnionType.of(
                                            StringType,
                                            ObjectType(
                                                linkedMapOf("name" to FieldType(StringType, true))
                                            )
                                        ),
                                        true
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
                    "array_of_unions" to
                        ArrayValue(
                            listOf(
                                StringValue("abc"),
                                ObjectValue(linkedMapOf("name" to StringValue("def")))
                            )
                        )
                )
            )

        val avroSchema = schema.toAvroSchema(stream.descriptor)
        val (recordMapped, _) = AvroMapperPipelineFactory().create(stream).map(record)
        val avroRecord = (recordMapped as ObjectValue).toAvroRecord(schema, avroSchema)

        Assertions.assertEquals(
            """{"id": "123", "array_of_unions": ["abc", {"name": "def"}]}""",
            avroRecord.toString()
        )
    }

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
                                    "object" to
                                        FieldType(
                                            ObjectType(
                                                linkedMapOf(
                                                    "object_id" to FieldType(StringType, true),
                                                    "metadata" to
                                                        FieldType(ObjectTypeWithoutSchema, true)
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

        val pipeline = AvroMapperPipelineFactory().create(stream)
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
