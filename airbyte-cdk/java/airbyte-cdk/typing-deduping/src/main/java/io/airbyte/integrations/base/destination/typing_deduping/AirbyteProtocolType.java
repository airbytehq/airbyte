/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Protocol types are ordered by precedence in the case of a Union that contains multiple types.
 * Priority is given to wider scope types over narrower ones. (Note that because of dedup logic in
 * {@link AirbyteType#fromJsonSchema(JsonNode)}, at most one string or date/time type can exist in a
 * Union.)
 */
public enum AirbyteProtocolType implements AirbyteType {

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

  private static AirbyteProtocolType matches(final String type) {
    try {
      return AirbyteProtocolType.valueOf(type.toUpperCase());
    } catch (final IllegalArgumentException e) {
      LOGGER.error(String.format("Could not find matching AirbyteProtocolType for \"%s\": %s", type, e));
      return UNKNOWN;
    }
  }

  // Extracts the appropriate protocol type from the representative JSON
  protected static AirbyteProtocolType fromJson(final JsonNode node) {
    // JSON could be a string (ex: "number")
    if (node.isTextual()) {
      return matches(node.asText());
    }

    // or, JSON could be a node with fields
    final JsonNode propertyType = node.get("type");
    final JsonNode airbyteType = node.get("airbyte_type");
    final JsonNode format = node.get("format");

    if (AirbyteType.nodeMatches(propertyType, "boolean")) {
      return BOOLEAN;
    } else if (AirbyteType.nodeMatches(propertyType, "integer")) {
      return INTEGER;
    } else if (AirbyteType.nodeMatches(propertyType, "number")) {
      return AirbyteType.nodeMatches(airbyteType, "integer") ? INTEGER : NUMBER;
    } else if (AirbyteType.nodeMatches(propertyType, "string")) {
      if (AirbyteType.nodeMatches(format, "date")) {
        return DATE;
      } else if (AirbyteType.nodeMatches(format, "time")) {
        if (AirbyteType.nodeMatches(airbyteType, "time_without_timezone")) {
          return TIME_WITHOUT_TIMEZONE;
        } else if (AirbyteType.nodeMatches(airbyteType, "time_with_timezone")) {
          return TIME_WITH_TIMEZONE;
        }
      } else if (AirbyteType.nodeMatches(format, "date-time")) {
        if (AirbyteType.nodeMatches(airbyteType, "timestamp_without_timezone")) {
          return TIMESTAMP_WITHOUT_TIMEZONE;
        } else if (airbyteType == null || AirbyteType.nodeMatches(airbyteType, "timestamp_with_timezone")) {
          return TIMESTAMP_WITH_TIMEZONE;
        }
      } else {
        return STRING;
      }
    }

    return UNKNOWN;
  }

}
