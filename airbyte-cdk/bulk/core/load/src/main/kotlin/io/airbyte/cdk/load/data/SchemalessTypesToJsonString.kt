/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToString

class SchemalessTypesToJsonString : AirbyteSchemaIdentityMapper {
    override fun mapObjectWithoutSchema(schema: ObjectTypeWithoutSchema): AirbyteType = StringType
    override fun mapObjectWithEmptySchema(schema: ObjectTypeWithEmptySchema): AirbyteType =
        StringType
    override fun mapArrayWithoutSchema(schema: ArrayTypeWithoutSchema): AirbyteType = StringType
}

class SchemalessValuesToJsonString : AirbyteValueIdentityMapper() {
    override fun mapObjectWithoutSchema(
        value: ObjectValue,
        schema: ObjectTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
    override fun mapObjectWithEmptySchema(
        value: ObjectValue,
        schema: ObjectTypeWithEmptySchema,
        context: Context
    ): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
    override fun mapArrayWithoutSchema(
        value: ArrayValue,
        schema: ArrayTypeWithoutSchema,
        context: Context
    ): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
    override fun mapUnknown(value: UnknownValue, context: Context): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
}
