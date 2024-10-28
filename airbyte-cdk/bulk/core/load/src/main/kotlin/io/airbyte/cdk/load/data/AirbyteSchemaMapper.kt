/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

interface AirbyteSchemaMapper {
    fun map(schema: AirbyteType): AirbyteType =
        when (schema) {
            is NullType -> mapNull(schema)
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

    fun mapField(field: FieldType): FieldType
    fun mapNull(schema: NullType): AirbyteType
    fun mapString(schema: StringType): AirbyteType
    fun mapBoolean(schema: BooleanType): AirbyteType
    fun mapInteger(schema: IntegerType): AirbyteType
    fun mapNumber(schema: NumberType): AirbyteType
    fun mapArray(schema: ArrayType): AirbyteType
    fun mapArrayWithoutSchema(schema: ArrayTypeWithoutSchema): AirbyteType
    fun mapObject(schema: ObjectType): AirbyteType
    fun mapObjectWithoutSchema(schema: ObjectTypeWithoutSchema): AirbyteType
    fun mapObjectWithEmptySchema(schema: ObjectTypeWithEmptySchema): AirbyteType
    fun mapUnion(schema: UnionType): AirbyteType
    fun mapDate(schema: DateType): AirbyteType
    fun mapTimeTypeWithTimezone(schema: TimeTypeWithTimezone): AirbyteType
    fun mapTimeTypeWithoutTimezone(schema: TimeTypeWithoutTimezone): AirbyteType
    fun mapTimestampTypeWithTimezone(schema: TimestampTypeWithTimezone): AirbyteType
    fun mapTimestampTypeWithoutTimezone(schema: TimestampTypeWithoutTimezone): AirbyteType
    fun mapUnknown(schema: UnknownType): AirbyteType
}
