package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.node.ObjectNode

abstract class JsonSchemaMapper<R> {
    fun mapSchema(schema: ObjectNode): R {
        val schemaType = AirbyteJsonSchemaType.fromJsonSchema(schema)

        return when (schemaType) {
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
        }
    }

    abstract fun mapObjectWithProperties(schema: ObjectNode): R
    abstract fun mapObjectWithoutProperties(schema: ObjectNode): R
    abstract fun mapArrayWithItems(schema: ObjectNode): R
    abstract fun mapArrayWithItem(schema: ObjectNode): R
    abstract fun mapArrayWithoutItems(schema: ObjectNode): R
    abstract fun mapDate(schema: ObjectNode): R
    abstract fun mapTimeWithoutTimezone(schema: ObjectNode): R
    abstract fun mapTimeWithTimezone(schema: ObjectNode): R
    abstract fun mapDateTimeWithTimezone(schema: ObjectNode): R
    abstract fun mapDateTimeWithoutTimezone(schema: ObjectNode): R
    abstract fun mapString(schema: ObjectNode): R
    abstract fun mapBinaryData(schema: ObjectNode): R
    abstract fun mapBoolean(schema: ObjectNode): R
    abstract fun mapInteger(schema: ObjectNode): R
    abstract fun mapNumber(schema: ObjectNode): R
    abstract fun mapCombined(schema: ObjectNode): R
    abstract fun mapUnion(schema: ObjectNode): R
}

