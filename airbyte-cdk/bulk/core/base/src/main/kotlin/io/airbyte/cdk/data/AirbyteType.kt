/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.data

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil
import io.airbyte.protocol.models.JsonSchemaType

/**
 * Union type which models the Airbyte field type schema.
 *
 * This maps to the subset of [JsonSchemaType] which is used in practice. Its main reason for
 * existing is to provide type-safety and convenient comparisons and string representations.
 */
sealed interface AirbyteType {
    /** Unwraps the underlying Airbyte protocol type object. */
    fun asJsonSchemaType(): JsonSchemaType

    /** Convenience method to generate the JSON Schema object. */
    fun asJsonSchema(): JsonNode = Jsons.valueToTree(asJsonSchemaType().jsonSchemaTypeMap)
}

data class ArrayAirbyteType(
    val item: AirbyteType,
) : AirbyteType {
    override fun asJsonSchemaType(): JsonSchemaType =
        JsonSchemaType.builder(JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.ARRAY)
            .withItems(item.asJsonSchemaType())
            .build()
}

enum class LeafAirbyteType(
    private val jsonSchemaType: JsonSchemaType,
) : AirbyteType {
    BOOLEAN(JsonSchemaType.BOOLEAN),
    STRING(JsonSchemaType.STRING),
    BINARY(JsonSchemaType.STRING_BASE_64),
    DATE(JsonSchemaType.STRING_DATE),
    TIME_WITH_TIMEZONE(JsonSchemaType.STRING_TIME_WITH_TIMEZONE),
    TIME_WITHOUT_TIMEZONE(JsonSchemaType.STRING_TIME_WITHOUT_TIMEZONE),
    TIMESTAMP_WITH_TIMEZONE(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE),
    TIMESTAMP_WITHOUT_TIMEZONE(JsonSchemaType.STRING_TIMESTAMP_WITHOUT_TIMEZONE),
    INTEGER(JsonSchemaType.INTEGER),
    NUMBER(JsonSchemaType.NUMBER),
    NULL(JsonSchemaType.NULL),
    JSONB(JsonSchemaType.JSONB),
    ;

    override fun asJsonSchemaType(): JsonSchemaType = jsonSchemaType
}
