/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*

private val LOGGER = KotlinLogging.logger {}
/**
 * Protocol types are ordered by precedence in the case of a Union that contains multiple types.
 * Priority is given to wider scope types over narrower ones. (Note that because of dedup logic in
 * [AirbyteType.fromJsonSchema], at most one string or date/time type can exist in a Union.)
 */
enum class AirbyteProtocolType : AirbyteType {
    STRING,
    DATE,
    TIME_WITHOUT_TIMEZONE,
    TIME_WITH_TIMEZONE,
    TIMESTAMP_WITHOUT_TIMEZONE,
    TIMESTAMP_WITH_TIMEZONE,
    NUMBER,
    INTEGER,
    BOOLEAN,
    UNKNOWN;

    override val typeName: String
        get() = this.name

    companion object {
        private fun matches(type: String): AirbyteProtocolType {
            try {
                return valueOf(type.uppercase(Locale.getDefault()))
            } catch (e: IllegalArgumentException) {
                LOGGER.error { "Could not find matching AirbyteProtocolType for \"$type\": $e" }
                return UNKNOWN
            }
        }

        // Extracts the appropriate protocol type from the representative JSON
        fun fromJson(node: JsonNode): AirbyteProtocolType {
            // JSON could be a string (ex: "number")
            if (node.isTextual) {
                return matches(node.asText())
            }

            // or, JSON could be a node with fields
            val propertyType = node["type"]
            val airbyteType = node["airbyte_type"]
            val format = node["format"]

            if (AirbyteType.Companion.nodeMatches(propertyType, "boolean")) {
                return BOOLEAN
            } else if (AirbyteType.Companion.nodeMatches(propertyType, "integer")) {
                return INTEGER
            } else if (AirbyteType.Companion.nodeMatches(propertyType, "number")) {
                return if (AirbyteType.Companion.nodeMatches(airbyteType, "integer")) INTEGER
                else NUMBER
            } else if (AirbyteType.Companion.nodeMatches(propertyType, "string")) {
                if (AirbyteType.Companion.nodeMatches(format, "date")) {
                    return DATE
                } else if (AirbyteType.Companion.nodeMatches(format, "time")) {
                    if (AirbyteType.Companion.nodeMatches(airbyteType, "time_without_timezone")) {
                        return TIME_WITHOUT_TIMEZONE
                    } else if (
                        AirbyteType.Companion.nodeMatches(airbyteType, "time_with_timezone")
                    ) {
                        return TIME_WITH_TIMEZONE
                    }
                } else if (AirbyteType.Companion.nodeMatches(format, "date-time")) {
                    if (
                        AirbyteType.Companion.nodeMatches(airbyteType, "timestamp_without_timezone")
                    ) {
                        return TIMESTAMP_WITHOUT_TIMEZONE
                    } else if (
                        airbyteType == null ||
                            AirbyteType.Companion.nodeMatches(
                                airbyteType,
                                "timestamp_with_timezone"
                            )
                    ) {
                        return TIMESTAMP_WITH_TIMEZONE
                    }
                } else {
                    return STRING
                }
            }

            return UNKNOWN
        }
    }
}
