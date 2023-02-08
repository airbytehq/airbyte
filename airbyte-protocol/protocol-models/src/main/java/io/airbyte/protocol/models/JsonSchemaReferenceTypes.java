/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import java.util.Set;

public class JsonSchemaReferenceTypes {

  public static final Set<String> PRIMITIVE_JSON_TYPES = ImmutableSet.of(
      "string",
      "number",
      "integer",
      "boolean");

  public static final String REF_KEY = "$ref";
  public static final String TYPE_KEY = "type";
  public static final String ONEOF_KEY = "oneOf";
  public static final String PROPERTIES_KEY = "properties";
  public static final String ITEMS_KEY = "items";
  public static final String OBJECT_TYPE = "object";
  public static final String ARRAY_TYPE = "array";

  public static final String WELL_KNOWN_TYPES_FILENAME = "WellKnownTypes.json";
  public static final String STRING_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/String";
  public static final String BINARY_DATA_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/BinaryData";
  public static final String NUMBER_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/Number";
  public static final String INTEGER_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/Integer";
  public static final String BOOLEAN_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/Boolean";
  public static final String DATE_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/Date";
  public static final String TIMESTAMP_WITH_TIMEZONE_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/TimestampWithTimezone";
  public static final String TIMESTAMP_WITHOUT_TIMEZONE_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/TimestampWithoutTimezone";
  public static final String TIME_WITH_TIMEZONE_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/TimeWithTimezone";
  public static final String TIME_WITHOUT_TIMEZONE_REFERENCE = WELL_KNOWN_TYPES_FILENAME + "#/definitions/TimeWithoutTimezone";

  /**
   * This is primarily useful for migrating from protocol v0 to v1. It provides a mapping from the old
   * style {airbyte_type: foo} to new style {$ref: WellKnownTypes#/definitions/Foo}.
   */
  public static final Map<String, String> LEGACY_AIRBYTE_PROPERY_TO_REFERENCE = ImmutableMap.of(
      "timestamp_with_timezone", TIMESTAMP_WITH_TIMEZONE_REFERENCE,
      "timestamp_without_timezone", TIMESTAMP_WITHOUT_TIMEZONE_REFERENCE,
      "time_with_timezone", TIME_WITH_TIMEZONE_REFERENCE,
      "time_without_timezone", TIME_WITHOUT_TIMEZONE_REFERENCE,
      "integer", INTEGER_REFERENCE,
      // these types never actually use airbyte_type, but including them for consistency
      "string", STRING_REFERENCE,
      "number", NUMBER_REFERENCE,
      "boolean", BOOLEAN_REFERENCE,
      "date", DATE_REFERENCE);

  public static final Map<String, ObjectNode> REFERENCE_TYPE_TO_OLD_TYPE = ImmutableMap.of(
      TIMESTAMP_WITH_TIMEZONE_REFERENCE,
      (ObjectNode) Jsons.deserialize(
          """
          {"type": "string", "airbyte_type": "timestamp_with_timezone", "format": "date-time"}
          """),
      TIMESTAMP_WITHOUT_TIMEZONE_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "string", "airbyte_type": "timestamp_without_timezone", "format": "date-time"}
          """),
      TIME_WITH_TIMEZONE_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "string", "airbyte_type": "time_with_timezone", "format": "time"}
          """),
      TIME_WITHOUT_TIMEZONE_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "string", "airbyte_type": "time_without_timezone", "format": "time"}
          """),
      DATE_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "string", "format": "date"}
          """),
      INTEGER_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "number", "airbyte_type": "integer"}
          """),
      NUMBER_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "number"}
          """),
      BOOLEAN_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "boolean"}
          """),
      STRING_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "string"}
          """),
      BINARY_DATA_REFERENCE, (ObjectNode) Jsons.deserialize(
          """
          {"type": "string", "contentEncoding": "base64"}
          """));

}
