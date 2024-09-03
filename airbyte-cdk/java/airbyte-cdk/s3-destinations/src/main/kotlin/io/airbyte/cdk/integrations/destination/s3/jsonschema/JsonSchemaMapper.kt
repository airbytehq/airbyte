/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.jsonschema

import com.fasterxml.jackson.databind.node.ObjectNode

abstract class JsonSchemaMapper {
    fun mapSchema(schema: ObjectNode): ObjectNode {
        val schemaType = AirbyteJsonSchemaType.fromJsonSchema(schema)

        return when (schemaType) {
            AirbyteJsonSchemaType.NULL -> mapNull(schema)
            AirbyteJsonSchemaType.OBJECT_WITH_PROPERTIES -> mapObjectWithProperties(schema)
            AirbyteJsonSchemaType.OBJECT_WITHOUT_PROPERTIES -> mapObjectWithoutProperties(schema)
            AirbyteJsonSchemaType.ARRAY_WITH_ITEMS -> mapArrayWithItems(schema)
            AirbyteJsonSchemaType.ARRAY_WITH_ITEM -> mapArrayWithItem(schema)
            AirbyteJsonSchemaType.ARRAY_WITHOUT_ITEMS -> mapArrayWithoutItems(schema)
            AirbyteJsonSchemaType.DATE -> mapDate(schema)
            AirbyteJsonSchemaType.TIME_WITHOUT_TIMEZONE -> mapTimeWithoutTimezone(schema)
            AirbyteJsonSchemaType.TIME_WITH_TIMEZONE -> mapTimeWithTimezone(schema)
            AirbyteJsonSchemaType.TIMESTAMP_WITH_TIMEZONE -> mapDateTimeWithTimezone(schema)
            AirbyteJsonSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> mapDateTimeWithoutTimezone(schema)
            AirbyteJsonSchemaType.STRING -> mapString(schema)
            AirbyteJsonSchemaType.BINARY_DATA -> mapBinaryData(schema)
            AirbyteJsonSchemaType.BOOLEAN -> mapBoolean(schema)
            AirbyteJsonSchemaType.INTEGER -> mapInteger(schema)
            AirbyteJsonSchemaType.NUMBER -> mapNumber(schema)
            AirbyteJsonSchemaType.COMBINED -> mapCombined(schema)
            AirbyteJsonSchemaType.UNION -> mapUnion(schema)
            AirbyteJsonSchemaType.UNKNOWN -> mapUnknown(schema)
        }
    }

    abstract fun mapNull(schema: ObjectNode): ObjectNode
    abstract fun mapObjectWithProperties(schema: ObjectNode): ObjectNode
    abstract fun mapObjectWithoutProperties(schema: ObjectNode): ObjectNode
    abstract fun mapArrayWithItems(schema: ObjectNode): ObjectNode
    abstract fun mapArrayWithItem(schema: ObjectNode): ObjectNode
    abstract fun mapArrayWithoutItems(schema: ObjectNode): ObjectNode
    abstract fun mapDate(schema: ObjectNode): ObjectNode
    abstract fun mapTimeWithoutTimezone(schema: ObjectNode): ObjectNode
    abstract fun mapTimeWithTimezone(schema: ObjectNode): ObjectNode
    abstract fun mapDateTimeWithTimezone(schema: ObjectNode): ObjectNode
    abstract fun mapDateTimeWithoutTimezone(schema: ObjectNode): ObjectNode
    abstract fun mapString(schema: ObjectNode): ObjectNode
    abstract fun mapBinaryData(schema: ObjectNode): ObjectNode
    abstract fun mapBoolean(schema: ObjectNode): ObjectNode
    abstract fun mapInteger(schema: ObjectNode): ObjectNode
    abstract fun mapNumber(schema: ObjectNode): ObjectNode
    abstract fun mapCombined(schema: ObjectNode): ObjectNode
    abstract fun mapUnion(schema: ObjectNode): ObjectNode
    abstract fun mapUnknown(schema: ObjectNode): ObjectNode
}
