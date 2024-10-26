/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

interface AirbyteValueMapper {
    fun collectFailure(path: List<String>)
    fun map(
        value: AirbyteValue,
        schema: AirbyteType,
        path: List<String> = emptyList()
    ): AirbyteValue =
        try {
            when (schema) {
                is ObjectType -> mapObject(value as ObjectValue, schema, path)
                is ObjectTypeWithoutSchema ->
                    mapObjectWithoutSchema(value as ObjectValue, schema, path)
                is ObjectTypeWithEmptySchema ->
                    mapObjectWithEmptySchema(value as ObjectValue, schema, path)
                is ArrayType -> mapArray(value as ArrayValue, schema, path)
                is ArrayTypeWithoutSchema ->
                    mapArrayWithoutSchema(value as ArrayValue, schema, path)
                is UnionType -> mapUnion(value, schema, path)
                is BooleanType -> mapBoolean(value as BooleanValue, path)
                is NumberType -> mapNumber(value as NumberValue, path)
                is StringType -> mapString(value as StringValue, path)
                is IntegerType -> mapInteger(value as IntegerValue, path)
                is DateType -> mapDate(value as DateValue, path)
                is TimeTypeWithTimezone -> mapTimeWithTimezone(value as TimeValue, path)
                is TimeTypeWithoutTimezone -> mapTimeWithoutTimezone(value as TimeValue, path)
                is TimestampTypeWithTimezone ->
                    mapTimestampWithTimezone(value as TimestampValue, path)
                is TimestampTypeWithoutTimezone ->
                    mapTimestampWithoutTimezone(value as TimestampValue, path)
                is NullType -> mapNull(path)
                is UnknownType -> mapUnknown(value as UnknownValue, path)
            }
        } catch (e: Exception) {
            collectFailure(path)
            mapNull(path)
        }

    fun mapObject(value: ObjectValue, schema: ObjectType, path: List<String>): AirbyteValue
    fun mapObjectWithoutSchema(
        value: ObjectValue,
        schema: ObjectTypeWithoutSchema,
        path: List<String>
    ): AirbyteValue
    fun mapObjectWithEmptySchema(
        value: ObjectValue,
        schema: ObjectTypeWithEmptySchema,
        path: List<String>
    ): AirbyteValue
    fun mapArray(value: ArrayValue, schema: ArrayType, path: List<String>): AirbyteValue
    fun mapArrayWithoutSchema(
        value: ArrayValue,
        schema: ArrayTypeWithoutSchema,
        path: List<String>
    ): AirbyteValue
    fun mapUnion(value: AirbyteValue, schema: UnionType, path: List<String>): AirbyteValue
    fun mapBoolean(value: BooleanValue, path: List<String>): AirbyteValue
    fun mapNumber(value: NumberValue, path: List<String>): AirbyteValue
    fun mapString(value: StringValue, path: List<String>): AirbyteValue
    fun mapInteger(value: IntegerValue, path: List<String>): AirbyteValue
    fun mapDate(value: DateValue, path: List<String>): AirbyteValue
    fun mapTimeWithTimezone(value: TimeValue, path: List<String>): AirbyteValue
    fun mapTimeWithoutTimezone(value: TimeValue, path: List<String>): AirbyteValue
    fun mapTimestampWithTimezone(value: TimestampValue, path: List<String>): AirbyteValue
    fun mapTimestampWithoutTimezone(value: TimestampValue, path: List<String>): AirbyteValue
    fun mapNull(path: List<String>): AirbyteValue
    fun mapUnknown(value: UnknownValue, path: List<String>): AirbyteValue
}
