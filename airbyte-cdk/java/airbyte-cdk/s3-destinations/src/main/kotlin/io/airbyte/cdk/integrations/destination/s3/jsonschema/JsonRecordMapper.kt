/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.jsonschema

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode

abstract class JsonRecordMapper<R> {
    fun mapRecordWithSchema(record: JsonNode?, schema: ObjectNode): R {
        val schemaType = AirbyteJsonSchemaType.fromJsonSchema(schema)

        return when (schemaType) {
            AirbyteJsonSchemaType.NULL -> mapNull(record, schema)
            AirbyteJsonSchemaType.BOOLEAN -> mapBoolean(record, schema)
            AirbyteJsonSchemaType.INTEGER -> mapInteger(record, schema)
            AirbyteJsonSchemaType.NUMBER -> mapNumber(record, schema)
            AirbyteJsonSchemaType.STRING -> mapString(record, schema)
            AirbyteJsonSchemaType.BINARY_DATA -> mapBinaryData(record, schema)
            AirbyteJsonSchemaType.DATE -> mapDate(record, schema)
            AirbyteJsonSchemaType.TIMESTAMP_WITH_TIMEZONE -> mapDateTimeWithTimezone(record, schema)
            AirbyteJsonSchemaType.TIMESTAMP_WITHOUT_TIMEZONE ->
                mapDateTimeWithoutTimezone(record, schema)
            AirbyteJsonSchemaType.TIME_WITH_TIMEZONE -> mapTimeWithTimezone(record, schema)
            AirbyteJsonSchemaType.TIME_WITHOUT_TIMEZONE -> mapTimeWithoutTimezone(record, schema)
            AirbyteJsonSchemaType.ARRAY_WITHOUT_ITEMS -> mapArrayWithoutItems(record, schema)
            AirbyteJsonSchemaType.ARRAY_WITH_ITEM -> mapArrayWithItem(record, schema)
            AirbyteJsonSchemaType.ARRAY_WITH_ITEMS -> mapArrayWithItems(record, schema)
            AirbyteJsonSchemaType.OBJECT_WITHOUT_PROPERTIES ->
                mapObjectWithoutProperties(record, schema)
            AirbyteJsonSchemaType.OBJECT_WITH_PROPERTIES -> mapObjectWithProperties(record, schema)
            AirbyteJsonSchemaType.UNION -> mapUnion(record, schema)
            AirbyteJsonSchemaType.COMBINED -> mapCombined(record, schema)
            AirbyteJsonSchemaType.UNKNOWN -> mapUnknown(record, schema)
        }
    }

    abstract fun mapNull(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapBoolean(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapInteger(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapNumber(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapString(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapBinaryData(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapDate(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapDateTimeWithTimezone(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapDateTimeWithoutTimezone(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapTimeWithTimezone(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapTimeWithoutTimezone(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapArrayWithoutItems(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapArrayWithItem(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapArrayWithItems(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapObjectWithoutProperties(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapObjectWithProperties(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapUnion(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapCombined(record: JsonNode?, schema: ObjectNode): R
    abstract fun mapUnknown(record: JsonNode?, schema: ObjectNode): R
}
