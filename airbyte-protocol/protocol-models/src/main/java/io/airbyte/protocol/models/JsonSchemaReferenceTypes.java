/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import java.util.Map;
import java.util.Set;

public class JsonSchemaReferenceTypes {

  public static final Set<String> PRIMITIVE_JSON_TYPES = ImmutableSet.of(
      "string",
      "number",
      "integer",
      "boolean");

  public static final String STRING_REFERENCE = "WellKnownTypes.json#/definitions/String";
  public static final String BINARY_DATA_REFERENCE = "WellKnownTypes.json#/definitions/BinaryData";
  public static final String NUMBER_REFERENCE = "WellKnownTypes.json#/definitions/Number";
  public static final String INTEGER_REFERENCE = "WellKnownTypes.json#/definitions/Integer";
  public static final String BOOLEAN_REFERENCE = "WellKnownTypes.json#/definitions/Boolean";
  public static final String DATE_REFERENCE = "WellKnownTypes.json#/definitions/Date";
  public static final String TIMESTAMP_WITH_TIMEZONE_REFERENCE = "WellKnownTypes.json#/definitions/TimestampWithTimezone";
  public static final String TIMESTAMP_WITHOUT_TIMEZONE_REFERENCE = "WellKnownTypes.json#/definitions/TimestampWithoutTimezone";
  public static final String TIME_WITH_TIMEZONE_REFERENCE = "WellKnownTypes.json#/definitions/TimeWithTimezone";
  public static final String TIME_WITHOUT_TIMEZONE_REFERENCE = "WellKnownTypes.json#/definitions/TimeWithoutTimezone";

  /**
   * This is primarily useful for migrating from protocol v0 to v1. It provides a mapping from the old
   * style {airbyte_type: foo} to new style {$ref: WellKnownTypes#/definitions/Foo}.
   */
  public static final Map<String, String> AIRBYTE_TYPE_TO_REFERENCE_TYPE = ImmutableMap.of(
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

}
