/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

open class AirbyteSchemaIdentityMapper : AirbyteSchemaMapper {
    override fun mapNull(schema: NullType): AirbyteType = schema
    override fun mapString(schema: StringType): AirbyteType = schema
    override fun mapBoolean(schema: BooleanType): AirbyteType = schema
    override fun mapInteger(schema: IntegerType): AirbyteType = schema
    override fun mapNumber(schema: NumberType): AirbyteType = schema
    override fun mapArray(schema: ArrayType): AirbyteType = schema
    override fun mapArrayWithoutSchema(schema: ArrayTypeWithoutSchema): AirbyteType = schema
    override fun mapObject(schema: ObjectType): AirbyteType = schema
    override fun mapObjectWithoutSchema(schema: ObjectTypeWithoutSchema): AirbyteType = schema
    override fun mapObjectWithEmptySchema(schema: ObjectTypeWithEmptySchema): AirbyteType = schema
    override fun mapUnion(schema: UnionType): AirbyteType = schema
    override fun mapDate(schema: DateType): AirbyteType = schema
    override fun mapTimeTypeWithTimezone(schema: TimeTypeWithTimezone): AirbyteType = schema
    override fun mapTimeTypeWithoutTimezone(schema: TimeTypeWithoutTimezone): AirbyteType = schema
    override fun mapTimestampTypeWithTimezone(schema: TimestampTypeWithTimezone): AirbyteType =
        schema
    override fun mapTimestampTypeWithoutTimezone(
        schema: TimestampTypeWithoutTimezone
    ): AirbyteType = schema
    override fun mapUnknown(schema: UnknownType): AirbyteType = schema
}
