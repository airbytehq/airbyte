package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.AirbyteProtocolType;

public class AirbyteTypeUtils {

  protected static boolean nodeIsType(final JsonNode node, final String type) {
    if (node == null || !node.isTextual()) {
      return false;
    }
    return node.toString().equals(type);
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
      if (nodeIsType(format, "date")) {
        return AirbyteProtocolType.DATE;
      } else if (nodeIsType(format, "time")) {
        if (nodeIsType(airbyteType, "timestamp_without_timezone")) {
          return AirbyteProtocolType.TIME_WITHOUT_TIMEZONE;
        } else if (nodeIsType(airbyteType, "timestamp_with_timezone")) {
          return AirbyteProtocolType.TIME_WITH_TIMEZONE;
        }
      } else if (nodeIsType(format, "date-time")) {
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

}
