/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.ArrayColumnType
import io.airbyte.cdk.discover.ColumnType
import io.airbyte.cdk.discover.LeafType

/**
 * Value type used to recursively re-generate the original [ColumnType] based on a catalog stream
 * field's JSON schema.
 */
@JvmInline
value class FieldSchema(private val jsonSchemaProperties: JsonNode) {

    fun value(key: String): String = jsonSchemaProperties[key]?.asText() ?: ""
    fun type(): String = value("type")
    fun format(): String = value("format")
    fun airbyteType(): String = value("airbyte_type")

    fun asColumnType(): ColumnType =
        when (type()) {
            "array" -> ArrayColumnType(FieldSchema(jsonSchemaProperties["items"]).asColumnType())
            "null" -> LeafType.NULL
            "boolean" -> LeafType.BOOLEAN
            "number" ->
                when (airbyteType()) {
                    "integer",
                    "big_integer" -> LeafType.INTEGER
                    else -> LeafType.NUMBER
                }
            "string" ->
                when (format()) {
                    "date" -> LeafType.DATE
                    "date-time" ->
                        if (airbyteType() == "timestamp_with_timezone") {
                            LeafType.TIMESTAMP_WITH_TIMEZONE
                        } else {
                            LeafType.TIMESTAMP_WITHOUT_TIMEZONE
                        }
                    "time" ->
                        if (airbyteType() == "time_with_timezone") {
                            LeafType.TIME_WITH_TIMEZONE
                        } else {
                            LeafType.TIME_WITHOUT_TIMEZONE
                        }
                    else ->
                        if (value("contentEncoding") == "base64") {
                            LeafType.BINARY
                        } else {
                            LeafType.STRING
                        }
                }
            else -> LeafType.JSONB
        }
}
