/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToString

// TODO: S3V2 Remove this
class SchemalessTypesToJsonString : AirbyteSchemaIdentityMapper {
    override fun mapObjectWithoutSchema(schema: ObjectTypeWithoutSchema): AirbyteType = StringType
    override fun mapObjectWithEmptySchema(schema: ObjectTypeWithEmptySchema): AirbyteType =
        StringType
    override fun mapArrayWithoutSchema(schema: ArrayTypeWithoutSchema): AirbyteType = StringType
    override fun mapUnknown(schema: UnknownType): AirbyteType = StringType
}

class SchemalessValuesToJsonString : AirbyteValueIdentityMapper() {
    override fun mapObjectWithoutSchema(
        value: AirbyteValue,
        schema: ObjectTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
    override fun mapObjectWithEmptySchema(
        value: AirbyteValue,
        schema: ObjectTypeWithEmptySchema,
        context: Context
    ): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
    override fun mapArrayWithoutSchema(
        value: AirbyteValue,
        schema: ArrayTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
    override fun mapUnknown(value: UnknownValue, context: Context): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context

    override fun mapUnion(
        value: AirbyteValue,
        schema: UnionType,
        context: Context
    ): Pair<AirbyteValue, Context> {
        if (ObjectTypeWithEmptySchema in schema.options && value is ObjectValue) {
            return mapObjectWithEmptySchema(value, ObjectTypeWithEmptySchema, context)
        }

        if (ObjectTypeWithoutSchema in schema.options && value is ObjectValue) {
            return mapObjectWithoutSchema(value, ObjectTypeWithoutSchema, context)
        }

        if (ArrayTypeWithoutSchema in schema.options && value is ArrayValue) {
            return mapArrayWithoutSchema(value, ArrayTypeWithoutSchema, context)
        }

        if (schema.options.any { it is UnknownType } && value is UnknownValue) {
            return mapUnknown(value, context)
        }

        return super.mapUnion(value, schema, context)
    }
}
