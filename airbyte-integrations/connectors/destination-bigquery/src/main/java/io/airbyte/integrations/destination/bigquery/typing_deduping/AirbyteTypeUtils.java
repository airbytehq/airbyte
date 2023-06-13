package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;

public class AirbyteTypeUtils {

  protected static class JsonSchemaDefinition {
    JsonNode propertyType;
    JsonNode airbyteType;
    JsonNode format;

    protected JsonSchemaDefinition(final JsonNode propertyType,
                                final JsonNode airbyteType,
                                final JsonNode format) {
      this.propertyType = propertyType;
      this.airbyteType = airbyteType;
      this.format = format;
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

  private static boolean nodeMatchesTextualType(final JsonNode node, final String type) {
    if (node == null || !node.isTextual()) {
      return false;
    }
    return node.toString().equals(type);
  }

  protected static boolean isString(final JsonSchemaDefinition definition) {
    return nodeMatchesType(definition.propertyType, "string");
  }

  protected static boolean isDatetime(final JsonSchemaDefinition definition) {
    return isString(definition) && nodeMatchesType(definition.format, "date-time");
  }

  protected static boolean isDatetimeWithoutTimezone(final JsonSchemaDefinition definition) {
    return isDatetime(definition) && nodeMatchesTextualType(definition.airbyteType, "timestamp_without_timezone");
  }

  protected static boolean isDatetimeWithTimezone(final JsonSchemaDefinition definition) {
    return isDatetime(definition) &&
        (definition.airbyteType == null ||
            nodeMatchesTextualType(definition.airbyteType, "timestamp_with_timezone"));
  }

  protected static boolean isDate(final JsonSchemaDefinition definition) {
    return isString(definition) && nodeMatchesType(definition.format, "date");
  }

  protected static boolean isTime(final JsonSchemaDefinition definition) {
    return isString(definition) && nodeMatchesTextualType(definition.format, "time");
  }

  protected static boolean isTimeWithTimezone(final JsonSchemaDefinition definition) {
    return isTime(definition) && nodeMatchesTextualType(definition.airbyteType, "time_with_timezone");
  }

  protected static boolean isTimeWithoutTimezone(final JsonSchemaDefinition definition) {
    return isTime(definition) && nodeMatchesTextualType(definition.airbyteType, "time_without_timezone");
  }

  protected static boolean isNumber(final JsonSchemaDefinition definition) {
    // Handle union type, give priority to wider scope types
    return !isString(definition) && nodeMatchesType(definition.propertyType, "number");
  }

  protected static boolean isBigInteger(final JsonSchemaDefinition definition) {
    return nodeMatchesType(definition.airbyteType, "big_integer");
  }

  protected static boolean isLong(final JsonSchemaDefinition definition) {
    // Check specifically for {type: number, airbyte_type: integer}
    if (nodeMatchesType(definition.propertyType, "number")
        && nodeMatchesTextualType(definition.airbyteType, "integer")) {
      return true;
    }
    // Handle union type, give priority to wider scope types
    return !isString(definition) && !isNumber(definition) && nodeMatchesType(definition.propertyType, "integer");
  }

  protected static boolean isBoolean(final JsonSchemaDefinition definition) {
    // Handle union type, give priority to wider scope types
    return !isString(definition) && !isNumber(definition)
        && !isBigInteger(definition) && !isLong(definition)
        && nodeMatchesType(definition.propertyType, "boolean");
  }

  protected static boolean isArray(final JsonNode type) {
    return nodeMatchesType(type, "array");
  }

  protected static boolean isObject(final JsonNode type) {
    return nodeMatchesType(type, "object");
  }

}
