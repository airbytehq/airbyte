/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueIdentityMapper
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToString

class IcebergStringifyComplexTypes :
    AirbyteValueIdentityMapper(recurseIntoObjects = false, recurseIntoUnions = false) {
    override fun mapObject(
        value: AirbyteValue,
        schema: ObjectType,
        context: Context
    ): Pair<AirbyteValue, Context> {
        if (context.path.isEmpty()) {
            return super.mapObject(value, schema, context)
        }
        return StringValue(value.serializeToString()) to context
    }

    override fun mapUnion(
        value: AirbyteValue,
        schema: UnionType,
        context: Context
    ): Pair<AirbyteValue, Context> {
        return StringValue(value.serializeToString()) to context
    }

    // These were copied out of SchemalessTypesToJsonString.
    // We can't directly use that class, because it recurses into objects,
    // which means it nulls out invalid values / prunes undeclared fields.
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
    override fun mapUnknown(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
}
