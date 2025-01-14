/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.icerberg.parquet

import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.data.iceberg.parquet.AirbyteTypeToIcebergSchema
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.protocol.models.Jsons
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class AirbyteTypeToIcebergSchemaTest {

    private val converter = AirbyteTypeToIcebergSchema()

    @Test
    fun `convert handles ObjectType`() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, false),
                    "name" to FieldType(StringType, true),
                ),
            )
        val result = converter.convert(objectType, stringifyObjects = false) as Types.StructType

        assertEquals(2, result.fields().size)
        val idField = result.field("id")
        val nameField = result.field("name")

        assertNotNull(idField)
        assertFalse(idField.isOptional)
        assertEquals(Types.LongType.get(), idField.type())

        assertNotNull(nameField)
        assertTrue(nameField.isOptional)
        assertEquals(Types.StringType.get(), nameField.type())
    }

    @Test
    fun `convert handles stringifying ObjectType`() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, false),
                    "name" to FieldType(StringType, true),
                ),
            )
        val result = converter.convert(objectType, stringifyObjects = true)

        assertEquals(Types.StringType.get(), result)
    }

    @Test
    fun `convert handles ArrayType`() {
        val arrayType = ArrayType(FieldType(IntegerType, false))
        val result = converter.convert(arrayType, stringifyObjects = false) as Types.ListType

        assertEquals(Types.LongType.get(), result.elementType())
        assertFalse(result.isElementOptional)
    }

    @Test
    fun `convert handles ArrayType with nullable items`() {
        val arrayType = ArrayType(FieldType(StringType, true))
        val result = converter.convert(arrayType, stringifyObjects = false) as Types.ListType

        assertEquals(Types.StringType.get(), result.elementType())
        assertTrue(result.isElementOptional)
    }

    @Test
    fun `convert throws exception for ArrayTypeWithoutSchema`() {
        assertThrows<IllegalArgumentException> {
            converter.convert(ArrayTypeWithoutSchema, stringifyObjects = false)
        }
    }

    @Test
    fun `convert handles BooleanType`() {
        assertEquals(
            Types.BooleanType.get(),
            converter.convert(BooleanType, stringifyObjects = false)
        )
    }

    @Test
    fun `convert handles DateType`() {
        assertEquals(Types.DateType.get(), converter.convert(DateType, stringifyObjects = false))
    }

    @Test
    fun `convert handles IntegerType`() {
        assertEquals(Types.LongType.get(), converter.convert(IntegerType, stringifyObjects = false))
    }

    @Test
    fun `convert handles NumberType`() {
        assertEquals(
            Types.DoubleType.get(),
            converter.convert(NumberType, stringifyObjects = false)
        )
    }

    @Test
    fun `convert throws exception for ObjectTypeWithEmptySchema`() {
        assertThrows<IllegalArgumentException> {
            converter.convert(ObjectTypeWithEmptySchema, stringifyObjects = false)
        }
    }

    @Test
    fun `convert throws exception for ObjectTypeWithoutSchema`() {
        assertThrows<IllegalArgumentException> {
            converter.convert(ObjectTypeWithoutSchema, stringifyObjects = false)
        }
    }

    @Test
    fun `convert handles StringType`() {
        assertEquals(
            Types.StringType.get(),
            converter.convert(StringType, stringifyObjects = false)
        )
    }

    @Test
    fun `convert handles TimeTypeWithTimezone`() {
        assertEquals(
            Types.TimeType.get(),
            converter.convert(TimeTypeWithTimezone, stringifyObjects = false)
        )
    }

    @Test
    fun `convert handles TimeTypeWithoutTimezone`() {
        assertEquals(
            Types.TimeType.get(),
            converter.convert(TimeTypeWithoutTimezone, stringifyObjects = false)
        )
    }

    @Test
    fun `convert handles TimestampTypeWithTimezone`() {
        assertEquals(
            Types.TimestampType.withZone(),
            converter.convert(TimestampTypeWithTimezone, stringifyObjects = false)
        )
    }

    @Test
    fun `convert handles TimestampTypeWithoutTimezone`() {
        assertEquals(
            Types.TimestampType.withoutZone(),
            converter.convert(TimestampTypeWithoutTimezone, stringifyObjects = false)
        )
    }

    @Test
    fun `convert handles UnionType with single option`() {
        val unionType = UnionType(setOf(IntegerType))
        val result = converter.convert(unionType, stringifyObjects = false) as Types.ListType

        assertEquals(Types.LongType.get(), result.elementType())
        assertTrue(result.isElementOptional)
    }

    @Test
    fun `convert handles UnionType with multiple options`() {
        val unionType = UnionType(setOf(StringType, IntegerType))
        val result = converter.convert(unionType, stringifyObjects = false) as Types.ListType

        assertEquals(Types.StringType.get(), result.elementType())
        assertTrue(result.isElementOptional)
    }

    @Test
    fun `convert handles UnknownType`() {
        assertEquals(
            Types.StringType.get(),
            converter.convert(UnknownType(Jsons.emptyObject()), stringifyObjects = false)
        )
    }

    @Test
    fun `toIcebergSchema handles ObjectType`() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "age" to FieldType(IntegerType, false),
                    "email" to FieldType(StringType, true),
                ),
            )
        val schema = objectType.toIcebergSchema(mutableListOf(mutableListOf("age")))

        assertEquals(2, schema.columns().size)
        val ageColumn = schema.findField("age")
        val emailColumn = schema.findField("email")

        assertNotNull(ageColumn)
        assertFalse(ageColumn!!.isOptional)
        assertEquals(Types.LongType.get(), ageColumn.type())

        assertNotNull(emailColumn)
        assertTrue(emailColumn!!.isOptional)
        assertEquals(Types.StringType.get(), emailColumn.type())

        val identifierFieldIds = schema.identifierFieldIds()
        assertEquals(1, identifierFieldIds.size)
        assertEquals(true, identifierFieldIds.contains(ageColumn.fieldId()))
    }
}
