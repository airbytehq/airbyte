package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.OneOf;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Struct;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class AirbyteTypeUtils {

  protected static boolean nodeIsType(final JsonNode node, final String type) {
    if (node == null || !node.isTextual()) {
      return false;
    }
    return node.toString().equals(type);
  }

  private static boolean nodeIsOrContainsType(final JsonNode node, final String type) {
    if (node == null) {
      return false;
    } else if (node.isTextual()) {
      return node.toString().equals(type);
    } else if (node.isArray()) {
      for (final JsonNode element : node) {
        if (element.toString().equals(type)) {
          return true;
        }
      }
    }
    return false;
  }

  protected static AirbyteType getAirbyteProtocolType(final JsonNode node) {
    final JsonNode propertyType = node.get("type");
    final JsonNode airbyteType = node.get("airbyte_type");
    final JsonNode format = node.get("format");

    if (nodeIsType(propertyType, "boolean")) {
      return AirbyteProtocolType.BOOLEAN;
    } else if (nodeIsType(propertyType, "integer")) {
      return AirbyteProtocolType.INTEGER;
    } else if (nodeIsType(propertyType, "number")) {
      if (nodeIsType(airbyteType, "integer")) {
        return AirbyteProtocolType.INTEGER;
      } else {
        return AirbyteProtocolType.NUMBER;
      }
    } else if (nodeIsType(propertyType, "string")) {
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

  // Map from a protocol type to what other protocol types should take precedence over it if present
  private static final Map<AirbyteProtocolType, List<AirbyteProtocolType>> EXCLUDED_PROTOCOL_TYPES_MAP = ImmutableMap.of(
      AirbyteProtocolType.BOOLEAN, ImmutableList.of(AirbyteProtocolType.STRING, AirbyteProtocolType.NUMBER, AirbyteProtocolType.INTEGER),
      AirbyteProtocolType.INTEGER, ImmutableList.of(AirbyteProtocolType.STRING, AirbyteProtocolType.NUMBER),
      AirbyteProtocolType.NUMBER, ImmutableList.of(AirbyteProtocolType.STRING)
  );

  // Protocol types in order of precedence
  private static final List<AirbyteProtocolType> ORDERED_PROTOCOL_TYPES_LIST = ImmutableList.of(
      AirbyteProtocolType.BOOLEAN,
      AirbyteProtocolType.INTEGER,
      AirbyteProtocolType.NUMBER,
      AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE,
      AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE,
      AirbyteProtocolType.DATE,
      AirbyteProtocolType.TIME_WITH_TIMEZONE,
      AirbyteProtocolType.TIME_WITHOUT_TIMEZONE,
      AirbyteProtocolType.STRING
  );

  // Pick which type in the list has precedence
  protected static AirbyteType chooseOneOfType(final OneOf o) {
    final List<AirbyteType> options = o.options();

    // record what types are present
    final Map<AirbyteProtocolType, Boolean> typePresenceMap = new HashMap<>();
    Arrays.stream(AirbyteProtocolType.values()).map(type -> typePresenceMap.put(type, false));
    Array foundArrayType = null;
    Struct foundStructType = null;

    // looping only once for efficiency
    for (final AirbyteType option : options) {
      if (option instanceof Array) {
        foundArrayType = (Array) option;
      } else if (option instanceof Struct) {
        foundStructType = (Struct) option;
      } else if (option instanceof final AirbyteProtocolType protocolType) {
        typePresenceMap.put(protocolType, true);
      }
    }

    if (foundArrayType != null) {
      return foundArrayType;
    } else if (foundStructType != null) {
      return foundStructType;
    } else {
      for (final AirbyteProtocolType protocolType : ORDERED_PROTOCOL_TYPES_LIST) {
        if (typePresenceMap.get(protocolType)) {
          boolean foundExcludedTypes = false;
          final List<AirbyteProtocolType> excludedTypes = EXCLUDED_PROTOCOL_TYPES_MAP.get(protocolType);
          for (final AirbyteProtocolType excludedType : excludedTypes) {
            if (typePresenceMap.get(excludedType)) {
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
