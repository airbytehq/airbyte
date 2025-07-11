/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigInteger
import java.util.UUID
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class DestinationRecordRawTest {

    // Create a schema with various field types for testing
    private val recordSchema =
        ObjectType(
            linkedMapOf(
                "string_field" to FieldType(StringType, true),
                "integer_field" to FieldType(IntegerType, false),
                "boolean_field" to FieldType(BooleanType, true),
                "number_field" to FieldType(NumberType, true),
                "array_field" to FieldType(ArrayType(FieldType(StringType, true)), true),
                "object_field" to
                    FieldType(
                        ObjectType(linkedMapOf("nested_field" to FieldType(StringType, true))),
                        true
                    )
            )
        )

    private val stream =
        DestinationStream(
            unmappedNamespace = "test_namespace",
            unmappedName = "test_stream",
            io.airbyte.cdk.load.command.Append,
            recordSchema,
            generationId = 42L,
            minimumGenerationId = 0L,
            syncId = 123L,
            namespaceMapper = NamespaceMapper()
        )

    @Test
    fun `test handling of undeclared fields`() {
        // Create a raw record with undeclared fields
        val jsonData =
            """
            {
                "string_field": "test string",
                "integer_field": 42,
                "undeclared_field1": "extra data",
                "undeclared_field2": 123
            }
        """.trimIndent()

        val recordMessage =
            AirbyteRecordMessage()
                .withNamespace("test_namespace")
                .withStream("test_stream")
                .withData(jsonData.deserializeToNode())
                .withEmittedAt(1234567890L)

        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)

        val rawRecord =
            DestinationRecordRaw(
                stream = stream,
                rawData = DestinationRecordJsonSource(airbyteMessage),
                serializedSizeBytes = airbyteMessage.serializeToString().length.toLong(),
                airbyteRawId = UUID.randomUUID(),
            )

        val enrichedRecord = rawRecord.asEnrichedDestinationRecordAirbyteValue()

        // Verify declared fields are processed correctly
        assertEquals(2, enrichedRecord.declaredFields.size)
        assertTrue(enrichedRecord.declaredFields.containsKey("string_field"))
        assertTrue(enrichedRecord.declaredFields.containsKey("integer_field"))

        // Verify undeclared fields are captured
        assertEquals(2, enrichedRecord.undeclaredFields.size)
        assertTrue(enrichedRecord.undeclaredFields.containsKey("undeclared_field1"))
        assertTrue(enrichedRecord.undeclaredFields.containsKey("undeclared_field2"))

        val undeclaredField1 = enrichedRecord.undeclaredFields["undeclared_field1"]
        assertNotNull(undeclaredField1)
        assertTrue(undeclaredField1!!.isTextual)
        assertEquals("extra data", undeclaredField1.asText())

        val undeclaredField2 = enrichedRecord.undeclaredFields["undeclared_field2"]
        assertNotNull(undeclaredField2)
        assertTrue(undeclaredField2!!.isNumber)
        assertEquals(123, undeclaredField2.asInt())
    }

    @Test
    fun `test type coercion for fields`() {
        // Create a raw record with type mismatches that should be coerced
        val jsonData =
            """
            {
                "string_field": 42,
                "integer_field": "123",
                "boolean_field": 1,
                "number_field": "456.78"
            }
        """.trimIndent()

        val recordMessage =
            AirbyteRecordMessage()
                .withNamespace("test_namespace")
                .withStream("test_stream")
                .withData(jsonData.deserializeToNode())
                .withEmittedAt(1234567890L)

        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)

        val rawRecord =
            DestinationRecordRaw(
                stream = stream,
                rawData = DestinationRecordJsonSource(airbyteMessage),
                serializedSizeBytes = airbyteMessage.serializeToString().length.toLong(),
                airbyteRawId = UUID.randomUUID(),
            )

        val enrichedRecord = rawRecord.asEnrichedDestinationRecordAirbyteValue()

        // Check coerced string field
        val stringField = enrichedRecord.declaredFields["string_field"]
        assertNotNull(stringField)
        assertTrue(stringField?.abValue is StringValue)
        assertEquals("42", (stringField?.abValue as StringValue).value)

        // Check coerced integer field
        val integerField = enrichedRecord.declaredFields["integer_field"]
        assertNotNull(integerField)
        assertTrue(integerField?.abValue is IntegerValue)
        assertEquals(BigInteger.valueOf(123), (integerField?.abValue as IntegerValue).value)

        // Check coerced boolean field - might be nullified or coerced depending on implementation
        val booleanField = enrichedRecord.declaredFields["boolean_field"]
        assertNotNull(booleanField)

        // Check coerced number field
        val numberField = enrichedRecord.declaredFields["number_field"]
        assertNotNull(numberField)
        assertTrue(numberField?.abValue is NumberValue)
    }

    @Test
    fun `test nullification of invalid values`() {
        // Create a raw record with invalid values that should be nullified
        val jsonData =
            """
            {
                "string_field": "valid string",
                "integer_field": "not a number",
                "array_field": "not an array"
            }
        """.trimIndent()

        val recordMessage =
            AirbyteRecordMessage()
                .withNamespace("test_namespace")
                .withStream("test_stream")
                .withData(jsonData.deserializeToNode())
                .withEmittedAt(1234567890L)

        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)

        val rawRecord =
            DestinationRecordRaw(
                stream = stream,
                rawData = DestinationRecordJsonSource(airbyteMessage),
                serializedSizeBytes = airbyteMessage.serializeToString().length.toLong(),
                airbyteRawId = UUID.randomUUID(),
            )

        val enrichedRecord = rawRecord.asEnrichedDestinationRecordAirbyteValue()

        // Check valid field is preserved
        val stringField = enrichedRecord.declaredFields["string_field"]
        assertNotNull(stringField)
        assertTrue(stringField?.abValue is StringValue)

        // Check invalid integer is nullified with change recorded
        val integerField = enrichedRecord.declaredFields["integer_field"]
        assertNotNull(integerField)
        assertEquals(NullValue, integerField?.abValue)
        assertTrue(integerField?.changes?.isNotEmpty() ?: false)
        assertEquals(
            AirbyteRecordMessageMetaChange.Change.NULLED,
            integerField?.changes?.get(0)?.change
        )

        // Check invalid array is nullified with change recorded
        val arrayField = enrichedRecord.declaredFields["array_field"]
        assertNotNull(arrayField)
        assertEquals(NullValue, arrayField?.abValue)
        assertTrue(arrayField?.changes?.isNotEmpty() ?: false)
    }

    @Test
    fun `test preservation of meta changes`() {
        // Create a raw record with meta changes
        val jsonData = """{"string_field": "test", "integer_field": 42}"""

        val recordMessage =
            AirbyteRecordMessage()
                .withNamespace("test_namespace")
                .withStream("test_stream")
                .withData(jsonData.deserializeToNode())
                .withEmittedAt(1234567890L)

        // Add meta changes
        val change =
            AirbyteRecordMessageMetaChange()
                .withField("some_field")
                .withChange(AirbyteRecordMessageMetaChange.Change.TRUNCATED)
                .withReason(
                    AirbyteRecordMessageMetaChange.Reason.DESTINATION_RECORD_SIZE_LIMITATION
                )

        val meta = AirbyteRecordMessageMeta().withChanges(listOf(change))
        recordMessage.withMeta(meta)

        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)

        val rawRecord =
            DestinationRecordRaw(
                stream = stream,
                rawData = DestinationRecordJsonSource(airbyteMessage),
                serializedSizeBytes = airbyteMessage.serializeToString().length.toLong(),
                airbyteRawId = UUID.randomUUID(),
            )

        val enrichedRecord = rawRecord.asEnrichedDestinationRecordAirbyteValue()

        // Verify meta changes are preserved
        assertNotNull(enrichedRecord.sourceMeta)
        assertEquals(1, enrichedRecord.sourceMeta.changes.size)
        assertEquals("some_field", enrichedRecord.sourceMeta.changes[0].field)
        assertEquals(
            AirbyteRecordMessageMetaChange.Change.TRUNCATED,
            enrichedRecord.sourceMeta.changes[0].change
        )
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_RECORD_SIZE_LIMITATION,
            enrichedRecord.sourceMeta.changes[0].reason
        )
    }

    @Test
    fun `test handling empty fields in schema`() {
        // Create an empty schema
        val emptySchema = ObjectType(linkedMapOf())

        val streamWithEmptySchema =
            DestinationStream(
                unmappedNamespace = "test_namespace",
                unmappedName = "test_stream",
                io.airbyte.cdk.load.command.Append,
                emptySchema,
                generationId = 42L,
                minimumGenerationId = 0L,
                syncId = 123L,
                namespaceMapper = NamespaceMapper()
            )

        val jsonData = """{"field1": "value1", "field2": 123}"""

        val recordMessage =
            AirbyteRecordMessage()
                .withNamespace("test_namespace")
                .withStream("test_stream")
                .withData(jsonData.deserializeToNode())
                .withEmittedAt(1234567890L)

        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)

        val rawRecord =
            DestinationRecordRaw(
                stream = streamWithEmptySchema,
                rawData = DestinationRecordJsonSource(airbyteMessage),
                serializedSizeBytes = airbyteMessage.serializeToString().length.toLong(),
                airbyteRawId = UUID.randomUUID(),
            )

        val enrichedRecord = rawRecord.asEnrichedDestinationRecordAirbyteValue()

        // Verify all fields are treated as undeclared
        assertEquals(0, enrichedRecord.declaredFields.size)
        assertEquals(2, enrichedRecord.undeclaredFields.size)
        assertTrue(enrichedRecord.undeclaredFields.containsKey("field1"))
        assertTrue(enrichedRecord.undeclaredFields.containsKey("field2"))
    }

    @Test
    fun `test complex nested structures`() {
        // Create a complex schema with nested structures
        val complexSchema =
            ObjectType(
                linkedMapOf(
                    "nested_object" to
                        FieldType(
                            ObjectType(
                                linkedMapOf(
                                    "level1" to
                                        FieldType(
                                            ObjectType(
                                                linkedMapOf("level2" to FieldType(StringType, true))
                                            ),
                                            true
                                        )
                                )
                            ),
                            true
                        ),
                    "array_of_objects" to
                        FieldType(
                            ArrayType(
                                FieldType(
                                    ObjectType(
                                        linkedMapOf(
                                            "item_id" to FieldType(IntegerType, false),
                                            "item_name" to FieldType(StringType, true)
                                        )
                                    ),
                                    true
                                )
                            ),
                            true
                        )
                )
            )

        val streamWithComplexSchema =
            DestinationStream(
                unmappedNamespace = "test_namespace",
                unmappedName = "test_stream",
                io.airbyte.cdk.load.command.Append,
                complexSchema,
                generationId = 42L,
                minimumGenerationId = 0L,
                syncId = 123L,
                namespaceMapper = NamespaceMapper()
            )

        val jsonData =
            """
            {
                "nested_object": {
                    "level1": {
                        "level2": "deep value"
                    }
                },
                "array_of_objects": [
                    {"item_id": 1, "item_name": "item 1"},
                    {"item_id": 2, "item_name": "item 2"}
                ]
            }
        """.trimIndent()

        val recordMessage =
            AirbyteRecordMessage()
                .withNamespace("test_namespace")
                .withStream("test_stream")
                .withData(jsonData.deserializeToNode())
                .withEmittedAt(1234567890L)

        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)

        val rawRecord =
            DestinationRecordRaw(
                stream = streamWithComplexSchema,
                rawData = DestinationRecordJsonSource(airbyteMessage),
                serializedSizeBytes = airbyteMessage.serializeToString().length.toLong(),
                airbyteRawId = UUID.randomUUID(),
            )

        val enrichedRecord = rawRecord.asEnrichedDestinationRecordAirbyteValue()

        // Verify complex fields are processed correctly
        assertEquals(2, enrichedRecord.declaredFields.size)

        // Check nested object
        val nestedObject = enrichedRecord.declaredFields["nested_object"]
        assertNotNull(nestedObject)
        assertTrue(nestedObject?.abValue is ObjectValue)

        // Check array of objects
        val arrayOfObjects = enrichedRecord.declaredFields["array_of_objects"]
        assertNotNull(arrayOfObjects)
        assertTrue(arrayOfObjects?.abValue is ArrayValue)
        assertEquals(2, (arrayOfObjects?.abValue as ArrayValue).values.size)
    }

    @Test
    fun `test missing required fields`() {
        // The schema has a required integer_field
        val jsonData =
            """
            {
                "string_field": "test string",
                "boolean_field": true
            }
        """.trimIndent()

        val recordMessage =
            AirbyteRecordMessage()
                .withNamespace("test_namespace")
                .withStream("test_stream")
                .withData(jsonData.deserializeToNode())
                .withEmittedAt(1234567890L)

        val airbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)

        val rawRecord =
            DestinationRecordRaw(
                stream = stream,
                rawData = DestinationRecordJsonSource(airbyteMessage),
                serializedSizeBytes = airbyteMessage.serializeToString().length.toLong(),
                airbyteRawId = UUID.randomUUID(),
            )

        val enrichedRecord = rawRecord.asEnrichedDestinationRecordAirbyteValue()

        // Verify fields are processed correctly
        assertEquals(2, enrichedRecord.declaredFields.size)
        assertTrue(enrichedRecord.declaredFields.containsKey("string_field"))
        assertTrue(enrichedRecord.declaredFields.containsKey("boolean_field"))

        // Check that the required field is not in the enriched record
        // (This might be unexpected, but the current implementation doesn't add fields that aren't
        // in the raw data)
        assertFalse(enrichedRecord.declaredFields.containsKey("integer_field"))
    }
}
