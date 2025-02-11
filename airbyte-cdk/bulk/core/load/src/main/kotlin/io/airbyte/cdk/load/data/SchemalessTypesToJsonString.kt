/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToString

/**
 * Intended for Avro and Parquet Conversions and similar use cases.
 *
 * The contract is to serialize the values of schemaless and unknown types to a json string.
 *
 * Because there is no JsonBlob `AirbyteType`, we leave the types as-is and just serialize them. It
 * is expected that the serializer will know to expect strings for each type.
 *
 * This means there's no need for a type mapper, unless you also want to support some subset of the
 * Unknown types.
 *
 * For example, [FailOnAllUnknownTypesExceptNull] is used to add support for `{ "type": "null" }`
 */
class FailOnAllUnknownTypesExceptNull : AirbyteSchemaIdentityMapper {
    override fun mapUnknown(schema: UnknownType) =
        if (
            schema.schema.isObject &&
                ((schema.schema.get("type").isTextual &&
                    schema.schema.get("type").textValue() == "null") ||
                    (schema.schema.get("type").isArray &&
                        schema.schema.get("type").elements().asSequence().all {
                            it.isTextual && it.textValue() == "null"
                        }))
        ) {
            schema
        } else {
            throw IllegalStateException("Unknown type: $schema")
        }
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
    override fun mapUnknown(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> =
        value.toJson().serializeToString().let(::StringValue) to context
}
