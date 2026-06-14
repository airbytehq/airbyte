/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.icerberg.parquet

import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.data.iceberg.parquet.AirbyteTypeToIcebergSchema
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.protocol.models.Jsons
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class AirbyteTypeToIcebergSchemaTest {

    private val converter = AirbyteTypeToIcebergSchema()

    @Test
    fun `convert handles ObjectType with defined properties as StructType`() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, false),
                    "name" to FieldType(StringType, true),
                ),
            )
        val result = converter.convert(objectType) as Types.StructType

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
    fun `convert stringifies ObjectType with empty properties`() {
        val objectType = ObjectType(linkedMapOf())
        val result = converter.convert(objectType)

        assertEquals(Types.StringType.get(), result)
    }

    @Test
    fun `convert stringifies ObjectType when maxDepth is zero`() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, false),
                    "name" to FieldType(StringType, true),
                ),
            )
        val result = converter.convert(objectType, maxDepth = 0)

        assertEquals(Types.StringType.get(), result)
    }

    @Test
    fun `convert handles nested ObjectType with depth limiting`() {
        val innerObject =
            ObjectType(
                linkedMapOf(
                    "deep_field" to FieldType(StringType, false),
                ),
            )
        val outerObject =
            ObjectType(
                linkedMapOf(
                    "nested" to FieldType(innerObject, true),
                ),
            )

        // With maxDepth=2, outer is StructType, inner is also StructType
        val resultDepth2 = converter.convert(outerObject, maxDepth = 2) as Types.StructType
        val nestedField = resultDepth2.field("nested")
        assertNotNull(nestedField)
        assertTrue(nestedField.type().isStructType)
        val innerStruct = nestedField.type().asStructType()
        assertEquals(1, innerStruct.fields().size)
        assertEquals(Types.StringType.get(), innerStruct.field("deep_field").type())

        // With maxDepth=1, outer is StructType but inner becomes StringType
        val resultDepth1 = converter.convert(outerObject, maxDepth = 1) as Types.StructType
        val nestedFieldDepth1 = resultDepth1.field("nested")
        assertNotNull(nestedFieldDepth1)
        assertEquals(Types.StringType.get(), nestedFieldDepth1.type())
    }

    @Test
    fun `convert handles deeply nested ObjectType respecting depth 3`() {
        // depth 3: level1 -> level2 -> level3 -> level4 (stringified)
        val level4 = ObjectType(linkedMapOf("val" to FieldType(StringType, false)))
        val level3 = ObjectType(linkedMapOf("l4" to FieldType(level4, true)))
        val level2 = ObjectType(linkedMapOf("l3" to FieldType(level3, true)))
        val level1 = ObjectType(linkedMapOf("l2" to FieldType(level2, true)))

        val result = converter.convert(level1, maxDepth = 3) as Types.StructType

        // level1 -> StructType (depth=3)
        val l2Field = result.field("l2")
        assertTrue(l2Field.type().isStructType)

        // level2 -> StructType (depth=2)
        val l3Field = l2Field.type().asStructType().field("l3")
        assertTrue(l3Field.type().isStructType)

        // level3 -> StructType (depth=1)
        val l4Field = l3Field.type().asStructType().field("l4")
        // level4 is at depth=0 -> StringType (depth exhausted)
        assertEquals(Types.StringType.get(), l4Field.type())
    }

    @Test
    fun `convert handles ArrayType`() {
        val arrayType = ArrayType(FieldType(IntegerType, false))
        val result = converter.convert(arrayType) as Types.ListType

        assertEquals(Types.LongType.get(), result.elementType())
        assertFalse(result.isElementOptional)
    }

    @Test
    fun `convert handles ArrayType with nullable items`() {
        val arrayType = ArrayType(FieldType(StringType, true))
        val result = converter.convert(arrayType) as Types.ListType

        assertEquals(Types.StringType.get(), result.elementType())
        assertTrue(result.isElementOptional)
    }

    @Test
    fun `convert handles ArrayTypeWithoutSchema as StringType`() {
        val result = converter.convert(ArrayTypeWithoutSchema)
        assertEquals(Types.StringType.get(), result)
    }

    @Test
    fun `convert handles BooleanType`() {
        assertEquals(Types.BooleanType.get(), converter.convert(BooleanType))
    }

    @Test
    fun `convert handles DateType`() {
        assertEquals(Types.DateType.get(), converter.convert(DateType))
    }

    @Test
    fun `convert handles IntegerType`() {
        assertEquals(Types.LongType.get(), converter.convert(IntegerType))
    }

    @Test
    fun `convert handles NumberType`() {
        assertEquals(Types.DoubleType.get(), converter.convert(NumberType))
    }

    @Test
    fun `convert handles ObjectTypeWithEmptySchema as StringType`() {
        val result = converter.convert(ObjectTypeWithEmptySchema)
        assertEquals(Types.StringType.get(), result)
    }

    @Test
    fun `convert handles ObjectTypeWithoutSchema as StringType`() {
        val result = converter.convert(ObjectTypeWithoutSchema)
        assertEquals(Types.StringType.get(), result)
    }

    @Test
    fun `convert handles StringType`() {
        assertEquals(Types.StringType.get(), converter.convert(StringType))
    }

    @Test
    fun `convert handles TimeTypeWithTimezone`() {
        assertEquals(Types.TimeType.get(), converter.convert(TimeTypeWithTimezone))
    }

    @Test
    fun `convert handles TimeTypeWithoutTimezone`() {
        assertEquals(Types.TimeType.get(), converter.convert(TimeTypeWithoutTimezone))
    }

    @Test
    fun `convert handles TimestampTypeWithTimezone`() {
        assertEquals(Types.TimestampType.withZone(), converter.convert(TimestampTypeWithTimezone))
    }

    @Test
    fun `convert handles TimestampTypeWithoutTimezone`() {
        assertEquals(
            Types.TimestampType.withoutZone(),
            converter.convert(TimestampTypeWithoutTimezone)
        )
    }

    @Test
    fun `convert handles UnionType with single option`() {
        val unionType = UnionType(setOf(IntegerType), isLegacyUnion = false)
        val result = converter.convert(unionType) as Types.ListType

        assertEquals(Types.LongType.get(), result.elementType())
        assertTrue(result.isElementOptional)
    }

    @Test
    fun `convert handles UnionType with multiple options`() {
        val unionType = UnionType(setOf(StringType, IntegerType), isLegacyUnion = false)
        val result = converter.convert(unionType) as Types.ListType

        assertEquals(Types.StringType.get(), result.elementType())
        assertTrue(result.isElementOptional)
    }

    @Test
    fun `convert handles UnknownType`() {
        assertEquals(Types.StringType.get(), converter.convert(UnknownType(Jsons.emptyObject())))
    }

    @Test
    fun `toIcebergSchema handles ObjectType with struct fields`() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "age" to FieldType(IntegerType, false),
                    "email" to FieldType(StringType, true),
                    "address" to
                        FieldType(
                            ObjectType(
                                linkedMapOf(
                                    "street" to FieldType(StringType, true),
                                    "city" to FieldType(StringType, true),
                                )
                            ),
                            true,
                        ),
                ),
            )
        val schema = objectType.toIcebergSchema(mutableListOf(mutableListOf("age")))

        assertEquals(3, schema.columns().size)
        val ageColumn = schema.findField("age")
        val emailColumn = schema.findField("email")
        val addressColumn = schema.findField("address")

        assertNotNull(ageColumn)
        assertFalse(ageColumn!!.isOptional)
        assertEquals(Types.LongType.get(), ageColumn.type())

        assertNotNull(emailColumn)
        assertTrue(emailColumn!!.isOptional)
        assertEquals(Types.StringType.get(), emailColumn.type())

        // address should be a StructType since it has defined properties
        assertNotNull(addressColumn)
        assertTrue(addressColumn!!.isOptional)
        assertTrue(addressColumn.type().isStructType)
        val addressStruct = addressColumn.type().asStructType()
        assertEquals(2, addressStruct.fields().size)
        assertNotNull(addressStruct.field("street"))
        assertNotNull(addressStruct.field("city"))

        val identifierFieldIds = schema.identifierFieldIds()
        assertEquals(1, identifierFieldIds.size)
        assertEquals(true, identifierFieldIds.contains(ageColumn.fieldId()))
    }

    @Test
    fun `toIcebergSchema maps PK NumberType to StringType for identifier compatibility`() {
        val objectType =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(NumberType, false),
                    "amount" to FieldType(NumberType, true),
                ),
            )
        val schema = objectType.toIcebergSchema(mutableListOf(mutableListOf("id")))

        assertEquals(2, schema.columns().size)
        val idColumn = schema.findField("id")
        val amountColumn = schema.findField("amount")

        // PK NumberType field should be StringType (for Iceberg identifier compatibility)
        assertNotNull(idColumn)
        assertFalse(idColumn!!.isOptional)
        assertEquals(Types.StringType.get(), idColumn.type())

        // Non-PK NumberType field should remain DoubleType
        assertNotNull(amountColumn)
        assertTrue(amountColumn!!.isOptional)
        assertEquals(Types.DoubleType.get(), amountColumn.type())

        // PK field should be in identifier fields (StringType is allowed)
        val identifierFieldIds = schema.identifierFieldIds()
        assertEquals(1, identifierFieldIds.size)
        assertTrue(identifierFieldIds.contains(idColumn.fieldId()))
    }

    @Test
    fun `convert handles ObjectType with nested struct inside array`() {
        val innerObject =
            ObjectType(
                linkedMapOf(
                    "amount" to FieldType(NumberType, false),
                    "currency" to FieldType(StringType, false),
                ),
            )
        val arrayOfObjects = ArrayType(FieldType(innerObject, true))
        val result = converter.convert(arrayOfObjects) as Types.ListType

        assertTrue(result.elementType().isStructType)
        val elementStruct = result.elementType().asStructType()
        assertEquals(2, elementStruct.fields().size)
        assertEquals(Types.DoubleType.get(), elementStruct.field("amount").type())
        assertEquals(Types.StringType.get(), elementStruct.field("currency").type())
    }
}
