/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.avro.toAvroSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
import io.airbyte.cdk.load.message.Meta
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

class AirbyteTypeToAvroSchemaTest {
    @Test
    fun `test name mangling`() {
        val schema =
            ObjectType(
                properties =
                    linkedMapOf(
                        "1d_view" to FieldType(type = StringType, nullable = false),
                    )
            )
        val descriptor = DestinationStream.Descriptor("test", "stream")
        assertDoesNotThrow { schema.toAvroSchema(descriptor) }
    }

    @Test
    fun `test airbyte meta schema`() {
        val schema = ObjectType(linkedMapOf()).withAirbyteMeta()
        val descriptor = DestinationStream.Descriptor("test", "stream")
        val avroSchema = schema.toAvroSchema(descriptor)

        assertEquals(
            avroSchema.getField(Meta.COLUMN_NAME_AB_RAW_ID).schema().type,
            Schema.Type.STRING
        )
        assertEquals(
            avroSchema.getField(Meta.COLUMN_NAME_AB_RAW_ID).schema().logicalType,
            LogicalTypes.uuid()
        )
        assertEquals(
            avroSchema.getField(Meta.COLUMN_NAME_AB_EXTRACTED_AT).schema().type,
            Schema.Type.LONG
        )
        assertEquals(
            avroSchema.getField(Meta.COLUMN_NAME_AB_EXTRACTED_AT).schema().logicalType,
            LogicalTypes.timestampMillis()
        )
        assertEquals(
            avroSchema.getField(Meta.COLUMN_NAME_AB_GENERATION_ID).schema().type,
            Schema.Type.LONG
        )

        val metaSchema = avroSchema.getField(Meta.COLUMN_NAME_AB_META).schema()
        assertEquals(metaSchema.type, Schema.Type.RECORD)
        assertEquals(metaSchema.fields.size, 2)

        // Meta field 1
        val changesSchema = metaSchema.getField("changes").schema()
        assertEquals(changesSchema.type, Schema.Type.ARRAY)

        val changeSchema = changesSchema.elementType
        assertEquals(changeSchema.type, Schema.Type.RECORD)
        assertEquals(changeSchema.fields.size, 3)
        assertEquals(changeSchema.getField("field").schema().type, Schema.Type.STRING)
        assertEquals(changeSchema.getField("change").schema().type, Schema.Type.STRING)
        assertEquals(changeSchema.getField("reason").schema().type, Schema.Type.STRING)

        // Meta field 2
        assertEquals(metaSchema.getField("sync_id").schema().type, Schema.Type.LONG)
    }
}
