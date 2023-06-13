package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Array;

public class AirbyteTypeUtils {

  protected static class JsonSchemaDefinition {
    JsonNode propertyType;
    JsonNode airbyteType;
    JsonNode format;
    JsonNode items;

    protected JsonSchemaDefinition(final JsonNode node) {
      this.propertyType = node.get("type");
      this.airbyteType = node.get("airbyte_type");
      this.format = node.get("format");
      this.items = node.get("items");
    }
  }

  private static boolean nodeMatchesType(final JsonNode node, final String type) {
    if (node == null) {
      return false;
    } else if (node.isTextual()) {
      return node.toString().equals(type);
    } else if (node.isArray()) {
      for (final JsonNode itemNode : node) {
        if (itemNode.toString().equals(type)) {
          return true;
        }
      }
    }
    return false;
  }

  protected static boolean nodeMatchesTextualType(final JsonNode node, final String type) {
    if (node == null || !node.isTextual()) {
      return false;
    }
    return node.toString().equals(type);
  }

  private static boolean isString(final JsonSchemaDefinition definition) {
    return nodeMatchesType(definition.propertyType, "string");
  }

  private static boolean isDatetime(final JsonSchemaDefinition definition) {
    return isString(definition) && nodeMatchesType(definition.format, "date-time");
  }

  private static boolean isDatetimeWithoutTimezone(final JsonSchemaDefinition definition) {
    return isDatetime(definition) && nodeMatchesTextualType(definition.airbyteType, "timestamp_without_timezone");
  }

  private static boolean isDatetimeWithTimezone(final JsonSchemaDefinition definition) {
    return isDatetime(definition) &&
        (definition.airbyteType == null ||
            nodeMatchesTextualType(definition.airbyteType, "timestamp_with_timezone"));
  }

  private static boolean isDate(final JsonSchemaDefinition definition) {
    return isString(definition) && nodeMatchesType(definition.format, "date");
  }

  private static boolean isTime(final JsonSchemaDefinition definition) {
    return isString(definition) && nodeMatchesTextualType(definition.format, "time");
  }

  private static boolean isTimeWithTimezone(final JsonSchemaDefinition definition) {
    return isTime(definition) && nodeMatchesTextualType(definition.airbyteType, "time_with_timezone");
  }

  private static boolean isTimeWithoutTimezone(final JsonSchemaDefinition definition) {
    return isTime(definition) && nodeMatchesTextualType(definition.airbyteType, "time_without_timezone");
  }

  private static boolean isNumber(final JsonSchemaDefinition definition) {
    // Handle union type, give priority to wider scope types
    return !isString(definition) && nodeMatchesType(definition.propertyType, "number");
  }

  private static boolean isBigInteger(final JsonSchemaDefinition definition) {
    return nodeMatchesType(definition.airbyteType, "big_integer");
  }

  private static boolean isLong(final JsonSchemaDefinition definition) {
    // Check specifically for {type: number, airbyte_type: integer}
    if (nodeMatchesType(definition.propertyType, "number")
        && nodeMatchesTextualType(definition.airbyteType, "integer")) {
      return true;
    }
    // Handle union type, give priority to wider scope types
    return !isString(definition) && !isNumber(definition) && nodeMatchesType(definition.propertyType, "integer");
  }

  private static boolean isBoolean(final JsonSchemaDefinition definition) {
    // Handle union type, give priority to wider scope types
    return !isString(definition) && !isNumber(definition)
        && !isBigInteger(definition) && !isLong(definition)
        && nodeMatchesType(definition.propertyType, "boolean");
  }

  private static boolean isArray(final JsonSchemaDefinition definition) {
    return nodeMatchesType(definition.propertyType, "array");
  }

  private static boolean isObject(final JsonSchemaDefinition definition) {
    return nodeMatchesType(definition.propertyType, "object");
  }

  protected static AirbyteType getAirbyteType(final JsonSchemaDefinition definition) {
    // TODO handle oneOf, unsupportedOneOf types

    // Treat simple types from narrower to wider scope type: boolean < integer < number < string
    if (isArray(definition)) {
      final JsonSchemaDefinition itemDefinition = new JsonSchemaDefinition(definition.items);
      return new Array(getAirbyteType(itemDefinition));
    // TODO handle object type
    } else if (isBoolean(definition)) {
      return AirbyteProtocolType.BOOLEAN;
    } else if (isBigInteger(definition)) {
      return AirbyteProtocolType.INTEGER;
    } else if (isLong(definition)) {
      return AirbyteProtocolType.INTEGER;
    } else if (isNumber(definition)) {
      return AirbyteProtocolType.NUMBER;
    } else if (isDatetimeWithoutTimezone(definition)) {
      return AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE;
    } else if (isDatetimeWithTimezone(definition)) {
      return AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE;
    } else if (isDate(definition)) {
      return AirbyteProtocolType.DATE;
    } else if (isTimeWithTimezone(definition)) {
      return AirbyteProtocolType.TIME_WITH_TIMEZONE;
    } else if (isTimeWithoutTimezone(definition)) {
      return AirbyteProtocolType.TIME_WITHOUT_TIMEZONE;
    } else if (isString(definition)) {
      return AirbyteProtocolType.STRING;
    } else {
      return AirbyteProtocolType.UNKNOWN;
    }
  }

}
