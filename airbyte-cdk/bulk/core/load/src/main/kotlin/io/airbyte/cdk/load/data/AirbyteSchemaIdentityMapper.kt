/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

interface AirbyteSchemaMapper {
    fun map(schema: AirbyteType): AirbyteType
}

class AirbyteSchemaNoopMapper : AirbyteSchemaMapper {
    override fun map(schema: AirbyteType): AirbyteType = schema
}

interface AirbyteSchemaIdentityMapper : AirbyteSchemaMapper {
    override fun map(schema: AirbyteType): AirbyteType =
        when (schema) {
            is StringType -> mapString(schema)
            is BooleanType -> mapBoolean(schema)
            is IntegerType -> mapInteger(schema)
            is NumberType -> mapNumber(schema)
            is ArrayType -> mapArray(schema)
            is ArrayTypeWithoutSchema -> mapArrayWithoutSchema(schema)
            is ObjectType -> mapObject(schema)
            is ObjectTypeWithoutSchema -> mapObjectWithoutSchema(schema)
            is ObjectTypeWithEmptySchema -> mapObjectWithEmptySchema(schema)
            is UnionType -> mapUnion(schema)
            is DateType -> mapDate(schema)
            is TimeTypeWithTimezone -> mapTimeTypeWithTimezone(schema)
            is TimeTypeWithoutTimezone -> mapTimeTypeWithoutTimezone(schema)
            is TimestampTypeWithTimezone -> mapTimestampTypeWithTimezone(schema)
            is TimestampTypeWithoutTimezone -> mapTimestampTypeWithoutTimezone(schema)
            is UnknownType -> mapUnknown(schema)
        }

    fun mapString(schema: StringType): AirbyteType = schema
    fun mapBoolean(schema: BooleanType): AirbyteType = schema
    fun mapInteger(schema: IntegerType): AirbyteType = schema
    fun mapNumber(schema: NumberType): AirbyteType = schema
    fun mapArray(schema: ArrayType): AirbyteType {
        return ArrayType(mapField(schema.items))
    }
    fun mapArrayWithoutSchema(schema: ArrayTypeWithoutSchema): AirbyteType = schema
    fun mapObject(schema: ObjectType): AirbyteType {
        val properties = LinkedHashMap<String, FieldType>()
        schema.properties.forEach { (name, field) -> properties[name] = mapField(field) }
        return ObjectType(properties)
    }
    fun mapObjectWithoutSchema(schema: ObjectTypeWithoutSchema): AirbyteType = schema
    fun mapObjectWithEmptySchema(schema: ObjectTypeWithEmptySchema): AirbyteType = schema
    fun mapUnion(schema: UnionType): AirbyteType {
        return UnionType.of(schema.options.map { map(it) })
    }
    fun mapDate(schema: DateType): AirbyteType = schema
    fun mapTimeTypeWithTimezone(schema: TimeTypeWithTimezone): AirbyteType = schema
    fun mapTimeTypeWithoutTimezone(schema: TimeTypeWithoutTimezone): AirbyteType = schema
    fun mapTimestampTypeWithTimezone(schema: TimestampTypeWithTimezone): AirbyteType = schema
    fun mapTimestampTypeWithoutTimezone(schema: TimestampTypeWithoutTimezone): AirbyteType = schema

    fun mapUnknown(schema: UnknownType): AirbyteType = schema
    fun mapField(field: FieldType): FieldType = FieldType(map(field.type), field.nullable)
}
