/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.TextNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Struct;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteTypeUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteTypeUtils.class);

  // Map from a protocol type to what other protocol types should take precedence over it if present
  // in a OneOf
  private static final Map<AirbyteProtocolType, List<AirbyteProtocolType>> EXCLUDED_PROTOCOL_TYPES_MAP = ImmutableMap.of(
      AirbyteProtocolType.BOOLEAN, ImmutableList.of(AirbyteProtocolType.STRING, AirbyteProtocolType.NUMBER, AirbyteProtocolType.INTEGER),
      AirbyteProtocolType.INTEGER, ImmutableList.of(AirbyteProtocolType.STRING, AirbyteProtocolType.NUMBER),
      AirbyteProtocolType.NUMBER, ImmutableList.of(AirbyteProtocolType.STRING));

  // Protocol types in order of precedence
  private static final List<AirbyteProtocolType> ORDERED_PROTOCOL_TYPES = ImmutableList.of(
      AirbyteProtocolType.BOOLEAN,
      AirbyteProtocolType.INTEGER,
      AirbyteProtocolType.NUMBER,
      AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE,
      AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE,
      AirbyteProtocolType.DATE,
      AirbyteProtocolType.TIME_WITH_TIMEZONE,
      AirbyteProtocolType.TIME_WITHOUT_TIMEZONE,
      AirbyteProtocolType.STRING);

  protected static boolean nodeIsType(final JsonNode node, final String type) {
    if (node == null || !node.isTextual()) {
      return false;
    }
    return node.equals(TextNode.valueOf(type));
  }

  private static boolean nodeIsOrContainsType(final JsonNode node, final String type) {
    if (node == null) {
      return false;
    } else if (node.isTextual()) {
      return nodeIsType(node, type);
    } else if (node.isArray()) {
      for (final JsonNode element : node) {
        if (nodeIsType(element, type)) {
          return true;
        }
      }
    }
    return false;
  }

  protected static AirbyteType getAirbyteProtocolType(final JsonNode node) {
    if (node.isTextual()) {
      return AirbyteProtocolType.matches(node.asText());
    }

    final JsonNode propertyType = node.get("type");
    final JsonNode airbyteType = node.get("airbyte_type");
    final JsonNode format = node.get("format");

    if (nodeIsOrContainsType(propertyType, "boolean")) {
      return AirbyteProtocolType.BOOLEAN;
    } else if (nodeIsOrContainsType(propertyType, "integer")) {
      return AirbyteProtocolType.INTEGER;
    } else if (nodeIsOrContainsType(propertyType, "number")) {
      if (nodeIsType(airbyteType, "integer")) {
        return AirbyteProtocolType.INTEGER;
      } else {
        return AirbyteProtocolType.NUMBER;
      }
    } else if (nodeIsOrContainsType(propertyType, "string")) {
      if (nodeIsOrContainsType(format, "date")) {
        return AirbyteProtocolType.DATE;
      } else if (nodeIsType(format, "time")) {
        if (nodeIsType(airbyteType, "timestamp_without_timezone")) {
          return AirbyteProtocolType.TIME_WITHOUT_TIMEZONE;
        } else if (nodeIsType(airbyteType, "timestamp_with_timezone")) {
          return AirbyteProtocolType.TIME_WITH_TIMEZONE;
        }
      } else if (nodeIsOrContainsType(format, "date-time")) {
        if (nodeIsType(airbyteType, "timestamp_without_timezone")) {
          return AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE;
        } else if (airbyteType == null || nodeIsType(airbyteType, "timestamp_with_timezone")) {
          return AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE;
        }
      } else {
        return AirbyteProtocolType.STRING;
      }
    }

    return AirbyteProtocolType.UNKNOWN;
  }

  // Pick which type in a OneOf has precedence
  public static AirbyteType chooseOneOfType(final OneOf o) {
    final List<AirbyteType> options = o.options();

    // record what types are present
    Array foundArrayType = null;
    Struct foundStructType = null;
    final Map<AirbyteProtocolType, Boolean> typePresenceMap = new HashMap<>();
    Arrays.stream(AirbyteProtocolType.values()).map(type -> typePresenceMap.put(type, false));

    // looping through the options only once for efficiency
    for (final AirbyteType option : options) {
      if (option instanceof final Array a) {
        foundArrayType = a;
      } else if (option instanceof final Struct s) {
        foundStructType = s;
      } else if (option instanceof final AirbyteProtocolType p) {
        typePresenceMap.put(p, true);
      }
    }

    if (foundArrayType != null) {
      return foundArrayType;
    } else if (foundStructType != null) {
      return foundStructType;
    } else {
      for (final AirbyteProtocolType protocolType : ORDERED_PROTOCOL_TYPES) {
        if (typePresenceMap.getOrDefault(protocolType, false)) {
          boolean foundExcludedTypes = false;
          final List<AirbyteProtocolType> excludedTypes = EXCLUDED_PROTOCOL_TYPES_MAP.getOrDefault(protocolType, Collections.emptyList());
          for (final AirbyteProtocolType excludedType : excludedTypes) {
            if (typePresenceMap.getOrDefault(excludedType, false)) {
              foundExcludedTypes = true;
              break;
            }
          }
          if (!foundExcludedTypes) {
            return protocolType;
          }
        }
      }
    }

    return AirbyteProtocolType.UNKNOWN;
  }

}
