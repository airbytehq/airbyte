/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.AirbyteType
import io.airbyte.cdk.discover.ArrayAirbyteType
import io.airbyte.cdk.discover.LeafAirbyteType

/**
 * Value type used to recursively re-generate the original [AirbyteType] based on a catalog stream
 * field's JSON schema.
 */
@JvmInline
value class FieldSchema(private val jsonSchemaProperties: JsonNode) {

    fun value(key: String): String = jsonSchemaProperties[key]?.asText() ?: ""
    fun type(): String = value("type")
    fun format(): String = value("format")
    fun airbyteType(): String = value("airbyte_type")

    fun asColumnType(): AirbyteType =
        when (type()) {
            "array" -> ArrayAirbyteType(FieldSchema(jsonSchemaProperties["items"]).asColumnType())
            "null" -> LeafAirbyteType.NULL
            "boolean" -> LeafAirbyteType.BOOLEAN
            "number" ->
                when (airbyteType()) {
                    "integer",
                    "big_integer" -> LeafAirbyteType.INTEGER
                    else -> LeafAirbyteType.NUMBER
                }
            "string" ->
                when (format()) {
                    "date" -> LeafAirbyteType.DATE
                    "date-time" ->
                        if (airbyteType() == "timestamp_with_timezone") {
                            LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE
                        } else {
                            LeafAirbyteType.TIMESTAMP_WITHOUT_TIMEZONE
                        }
                    "time" ->
                        if (airbyteType() == "time_with_timezone") {
                            LeafAirbyteType.TIME_WITH_TIMEZONE
                        } else {
                            LeafAirbyteType.TIME_WITHOUT_TIMEZONE
                        }
                    else ->
                        if (value("contentEncoding") == "base64") {
                            LeafAirbyteType.BINARY
                        } else {
                            LeafAirbyteType.STRING
                        }
                }
            else -> LeafAirbyteType.JSONB
        }
}
