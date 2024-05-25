/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.avro

import java.util.*
import javax.annotation.Nonnull
import org.apache.avro.Schema

/** Mapping of JsonSchema types to Avro types. */
enum class JsonSchemaType {
    STRING_V1("WellKnownTypes.json#/definitions/String", Schema.Type.STRING),
    INTEGER_V1("WellKnownTypes.json#/definitions/Integer", Schema.Type.LONG),
    NUMBER_V1("WellKnownTypes.json#/definitions/Number", Schema.Type.DOUBLE),
    BOOLEAN_V1("WellKnownTypes.json#/definitions/Boolean", Schema.Type.BOOLEAN),
    BINARY_DATA_V1("WellKnownTypes.json#/definitions/BinaryData", Schema.Type.BYTES),
    DATE_V1("WellKnownTypes.json#/definitions/Date", Schema.Type.INT),
    TIMESTAMP_WITH_TIMEZONE_V1(
        "WellKnownTypes.json#/definitions/TimestampWithTimezone",
        Schema.Type.LONG
    ),
    TIMESTAMP_WITHOUT_TIMEZONE_V1(
        "WellKnownTypes.json#/definitions/TimestampWithoutTimezone",
        Schema.Type.LONG
    ),
    TIME_WITH_TIMEZONE_V1("WellKnownTypes.json#/definitions/TimeWithTimezone", Schema.Type.STRING),
    TIME_WITHOUT_TIMEZONE_V1(
        "WellKnownTypes.json#/definitions/TimeWithoutTimezone",
        Schema.Type.LONG
    ),
    OBJECT("object", Schema.Type.RECORD),
    ARRAY("array", Schema.Type.ARRAY),
    COMBINED("combined", Schema.Type.UNION),
    @Deprecated("") STRING_V0("string", null, Schema.Type.STRING),
    @Deprecated("") NUMBER_INT_V0("number", "integer", Schema.Type.LONG),
    @Deprecated("") NUMBER_BIGINT_V0("string", "big_integer", Schema.Type.STRING),
    @Deprecated("") NUMBER_FLOAT_V0("number", "float", Schema.Type.FLOAT),
    @Deprecated("") NUMBER_V0("number", null, Schema.Type.DOUBLE),
    @Deprecated("") INTEGER_V0("integer", null, Schema.Type.LONG),
    @Deprecated("") BOOLEAN_V0("boolean", null, Schema.Type.BOOLEAN),
    @Deprecated("") NULL("null", null, Schema.Type.NULL);

    @JvmField val jsonSchemaType: String
    val avroType: Schema.Type
    var jsonSchemaAirbyteType: String? = null
        private set

    constructor(jsonSchemaType: String, jsonSchemaAirbyteType: String?, avroType: Schema.Type) {
        this.jsonSchemaType = jsonSchemaType
        this.jsonSchemaAirbyteType = jsonSchemaAirbyteType
        this.avroType = avroType
    }

    constructor(jsonSchemaType: String, avroType: Schema.Type) {
        this.jsonSchemaType = jsonSchemaType
        this.avroType = avroType
    }

    override fun toString(): String {
        return jsonSchemaType
    }

    companion object {
        @JvmStatic
        @JvmOverloads
        fun fromJsonSchemaType(
            @Nonnull jsonSchemaType: String,
            jsonSchemaAirbyteType: String? = null
        ): JsonSchemaType {
            var matchSchemaType: List<JsonSchemaType>? = null
            // Match by Type + airbyteType
            if (jsonSchemaAirbyteType != null) {
                matchSchemaType =
                    entries
                        .toTypedArray()
                        .filter { type: JsonSchemaType -> jsonSchemaType == type.jsonSchemaType }
                        .filter { type: JsonSchemaType ->
                            jsonSchemaAirbyteType == type.jsonSchemaAirbyteType
                        }
            }

            // Match by Type are no results already
            if (matchSchemaType == null || matchSchemaType.isEmpty()) {
                matchSchemaType =
                    entries.toTypedArray().filter { format: JsonSchemaType ->
                        jsonSchemaType == format.jsonSchemaType &&
                            format.jsonSchemaAirbyteType == null
                    }
            }

            require(!matchSchemaType.isEmpty()) {
                String.format(
                    "Unexpected jsonSchemaType - %s and jsonSchemaAirbyteType - %s",
                    jsonSchemaType,
                    jsonSchemaAirbyteType
                )
            }
            if (matchSchemaType.size > 1) {
                throw RuntimeException(
                    String.format(
                        "Match with more than one json type! Matched types : %s, Inputs jsonSchemaType : %s, jsonSchemaAirbyteType : %s",
                        matchSchemaType,
                        jsonSchemaType,
                        jsonSchemaAirbyteType
                    )
                )
            } else {
                return matchSchemaType[0]
            }
        }
    }
}
