package io.airbyte.protocol.models;

import com.google.common.collect.ImmutableMap;
import java.util.Map;

public class WellKnownTypesUtil {
  public enum WellKnownTypesPrimitive {
    STRING,
    BINARY_DATA,
    DATE,
    TIMESTAMP_WITH_TIMEZONE,
    TIMESTAMP_WITHOUT_TIMEZONE,
    TIME_WITH_TIMEZONE,
    TIME_WITHOUT_TIMEZONE,
    NUMBER,
    INTEGER,
    BOOLEAN
  }

  public static final Map<WellKnownTypesPrimitive, String> PRIMITIVE_TO_REFERENCE_TYPE =
      ImmutableMap.of(
          WellKnownTypesPrimitive.STRING, "WellKnownTypes.json#definitions/String",
          WellKnownTypesPrimitive.BINARY_DATA, "WellKnownTypes.json#definitions/BinaryData",
          WellKnownTypesPrimitive.DATE, "WellKnownTypes.json#definitions/Date",
          WellKnownTypesPrimitive.TIMESTAMP_WITH_TIMEZONE, "WellKnownTypes.json#definitions/TimestampWithTimezone",
          WellKnownTypesPrimitive.TIMESTAMP_WITHOUT_TIMEZONE, "WellKnownTypes.json#definitions/TimestampWithoutTimezone",
          WellKnownTypesPrimitive.TIME_WITH_TIMEZONE, "WellKnownTypes.json#definitions/TimeWithTimezone",
          WellKnownTypesPrimitive.TIME_WITHOUT_TIMEZONE, "WellKnownTypes.json#definitions/TimeWithoutTimezone",
          WellKnownTypesPrimitive.NUMBER, "WellKnownTypes.json#definitions/Number",
          WellKnownTypesPrimitive.INTEGER, "WellKnownTypes.json#definitions/Integer",
          WellKnownTypesPrimitive.BOOLEAN, "WellKnownTypes.json#definitions/Boolean"
      );
}
