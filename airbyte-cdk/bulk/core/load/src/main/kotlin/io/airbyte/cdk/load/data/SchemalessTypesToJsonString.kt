/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.util.serializeToString

class SchemalessTypesToJsonString : AirbyteSchemaIdentityMapper {
    override fun mapObjectWithoutSchema(schema: ObjectTypeWithoutSchema): AirbyteType = StringType
    override fun mapObjectWithEmptySchema(schema: ObjectTypeWithEmptySchema): AirbyteType =
        StringType
    override fun mapArrayWithoutSchema(schema: ArrayTypeWithoutSchema): AirbyteType = StringType
}

class SchemalessValuesToJsonString(meta: DestinationRecord.Meta) :
    AirbyteValueIdentityMapper(meta) {
    override fun mapObjectWithoutSchema(
        value: ObjectValue,
        schema: ObjectTypeWithoutSchema,
        path: List<String>
    ): AirbyteValue = value.toJson().serializeToString().let(::StringValue)
    override fun mapObjectWithEmptySchema(
        value: ObjectValue,
        schema: ObjectTypeWithEmptySchema,
        path: List<String>
    ): AirbyteValue = value.toJson().serializeToString().let(::StringValue)
    override fun mapArrayWithoutSchema(
        value: ArrayValue,
        schema: ArrayTypeWithoutSchema,
        path: List<String>
    ): AirbyteValue = value.toJson().serializeToString().let(::StringValue)
}
