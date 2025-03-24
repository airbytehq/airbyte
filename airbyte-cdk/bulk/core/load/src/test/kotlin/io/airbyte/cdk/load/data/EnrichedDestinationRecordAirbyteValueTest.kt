/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.EnrichedDestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class EnrichedDestinationRecordAirbyteValueTest {

    private val destinationStream =
        DestinationStream(
            descriptor = DestinationStream.Descriptor("test_namespace", "test_stream"),
            importType = Append,
            schema = ObjectTypeWithoutSchema,
            generationId = 42L,
            minimumGenerationId = 10L,
            syncId = 100L
        )

    private val emittedAtMs = 1234567890L

    @Test
    fun `test airbyteMetaFields property`() {
        val record =
            EnrichedDestinationRecordAirbyteValue(
                stream = destinationStream,
                declaredFields = emptyMap(),
                undeclaredFields = emptyMap(),
                emittedAtMs = emittedAtMs,
                meta = null
            )

        val metaFields = record.airbyteMetaFields

        // Should have exactly 4 meta fields
        assertEquals(4, metaFields.size)

        // Check that all required meta fields are present
        assertTrue(metaFields.containsKey(Meta.COLUMN_NAME_AB_RAW_ID))
        assertTrue(metaFields.containsKey(Meta.COLUMN_NAME_AB_EXTRACTED_AT))
        assertTrue(metaFields.containsKey(Meta.COLUMN_NAME_AB_META))
        assertTrue(metaFields.containsKey(Meta.COLUMN_NAME_AB_GENERATION_ID))

        // Check the types of meta fields
        val rawIdField = metaFields[Meta.COLUMN_NAME_AB_RAW_ID]!!
        assertTrue(rawIdField.abValue is StringValue)
        assertEquals(Meta.AirbyteMetaFields.RAW_ID.type, rawIdField.type)

        val extractedAtField = metaFields[Meta.COLUMN_NAME_AB_EXTRACTED_AT]!!
        assertTrue(extractedAtField.abValue is IntegerValue)
        assertEquals(emittedAtMs, (extractedAtField.abValue as IntegerValue).value.toLong())
        assertEquals(Meta.AirbyteMetaFields.EXTRACTED_AT.type, extractedAtField.type)

        val metaField = metaFields[Meta.COLUMN_NAME_AB_META]!!
        assertTrue(metaField.abValue is ObjectValue)
        val metaObj = metaField.abValue as ObjectValue
        assertEquals(2, metaObj.values.size)
        assertEquals(IntegerValue(destinationStream.syncId), metaObj.values["sync_id"])
        assertTrue(metaObj.values["changes"] is ArrayValue)
        assertEquals(Meta.AirbyteMetaFields.META.type, metaField.type)

        val generationIdField = metaFields[Meta.COLUMN_NAME_AB_GENERATION_ID]!!
        assertTrue(generationIdField.abValue is IntegerValue)
        assertEquals(
            destinationStream.generationId,
            (generationIdField.abValue as IntegerValue).value.toLong()
        )
        assertEquals(Meta.AirbyteMetaFields.GENERATION_ID.type, generationIdField.type)
    }

    @Test
    fun `test allTypedFields property`() {
        val declaredFields =
            mapOf(
                "field1" to
                    EnrichedAirbyteValue(
                        StringValue("value1"),
                        StringType,
                        "field1",
                        airbyteMetaField = null
                    ),
                "field2" to
                    EnrichedAirbyteValue(
                        IntegerValue(42),
                        IntegerType,
                        "field2",
                        airbyteMetaField = null
                    )
            )

        val record =
            EnrichedDestinationRecordAirbyteValue(
                stream = destinationStream,
                declaredFields = declaredFields,
                undeclaredFields = emptyMap(),
                emittedAtMs = emittedAtMs,
                meta = null
            )

        val allFields = record.allTypedFields

        // Should contain both declared fields and meta fields
        assertEquals(declaredFields.size + record.airbyteMetaFields.size, allFields.size)

        // Check that all declared fields are present
        declaredFields.forEach { (key, value) -> assertEquals(value, allFields[key]) }

        // Check that all meta fields are present
        record.airbyteMetaFields.forEach { (key, value) ->
            assertEquals(value.type, allFields[key]?.type)
            // Don't compare value directly for RAW_ID as it generates a random UUID
            if (key != Meta.COLUMN_NAME_AB_RAW_ID) {
                assertEquals(value.abValue::class, allFields[key]?.abValue!!::class)
            }
        }
    }

    @Test
    fun `test proper collection of changes in meta field`() {
        // Create fields with changes
        val field1 =
            EnrichedAirbyteValue(
                StringValue("value1"),
                StringType,
                "field1",
                airbyteMetaField = null
            )
        field1.truncate(Reason.DESTINATION_RECORD_SIZE_LIMITATION, StringValue("val"))

        val field2 =
            EnrichedAirbyteValue(
                IntegerValue(1000000),
                IntegerType,
                "field2",
                airbyteMetaField = null
            )
        field2.nullify(Reason.DESTINATION_FIELD_SIZE_LIMITATION)

        val declaredFields = mapOf("field1" to field1, "field2" to field2)

        // Create meta with its own changes
        val meta =
            Meta(
                changes =
                    listOf(
                        Meta.Change(
                            "meta_field",
                            Change.NULLED,
                            Reason.DESTINATION_SERIALIZATION_ERROR
                        )
                    )
            )

        val record =
            EnrichedDestinationRecordAirbyteValue(
                stream = destinationStream,
                declaredFields = declaredFields,
                undeclaredFields = emptyMap(),
                emittedAtMs = emittedAtMs,
                meta = meta
            )

        // Get the changes array from the meta field
        val metaField = record.airbyteMetaFields[Meta.COLUMN_NAME_AB_META]!!
        val metaObj = metaField.abValue as ObjectValue
        val changesArray = metaObj.values["changes"] as ArrayValue

        // Should contain 3 changes total: 1 from meta and 2 from declared fields
        assertEquals(3, changesArray.values.size)

        // Check each change
        val changeObjects = changesArray.values.filterIsInstance<ObjectValue>()

        // Find meta_field change
        val metaFieldChange =
            changeObjects.find { (it.values["field"] as StringValue).value == "meta_field" }
        assertNotNull(metaFieldChange)
        assertEquals("NULLED", (metaFieldChange!!.values["change"] as StringValue).value)
        assertEquals(
            "DESTINATION_SERIALIZATION_ERROR",
            (metaFieldChange.values["reason"] as StringValue).value
        )

        // Find field1 change
        val field1Change =
            changeObjects.find { (it.values["field"] as StringValue).value == "field1" }
        assertNotNull(field1Change)
        assertEquals("TRUNCATED", (field1Change!!.values["change"] as StringValue).value)
        assertEquals(
            "DESTINATION_RECORD_SIZE_LIMITATION",
            (field1Change.values["reason"] as StringValue).value
        )

        // Find field2 change
        val field2Change =
            changeObjects.find { (it.values["field"] as StringValue).value == "field2" }
        assertNotNull(field2Change)
        assertEquals("NULLED", (field2Change!!.values["change"] as StringValue).value)
        assertEquals(
            "DESTINATION_FIELD_SIZE_LIMITATION",
            (field2Change.values["reason"] as StringValue).value
        )
    }

    @Test
    fun `test UUID is generated for RAW_ID field`() {
        val record1 =
            EnrichedDestinationRecordAirbyteValue(
                stream = destinationStream,
                declaredFields = emptyMap(),
                undeclaredFields = emptyMap(),
                emittedAtMs = emittedAtMs,
                meta = null
            )

        val record2 =
            EnrichedDestinationRecordAirbyteValue(
                stream = destinationStream,
                declaredFields = emptyMap(),
                undeclaredFields = emptyMap(),
                emittedAtMs = emittedAtMs,
                meta = null
            )

        val rawId1 =
            (record1.airbyteMetaFields[Meta.COLUMN_NAME_AB_RAW_ID]!!.abValue as StringValue).value
        val rawId2 =
            (record2.airbyteMetaFields[Meta.COLUMN_NAME_AB_RAW_ID]!!.abValue as StringValue).value

        // Validate UUID format
        val uuidRegex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        assertTrue(rawId1.matches(Regex(uuidRegex)))
        assertTrue(rawId2.matches(Regex(uuidRegex)))

        // Two instances should have different UUIDs
        assertNotEquals(rawId1, rawId2)
    }
}
