/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import static io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.PRIMITIVE_TO_REFERENCE_BIMAP;

import com.google.common.collect.ImmutableMap;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import java.util.Map;
import java.util.Objects;

/**
 * Represents an Airbyte type. This corresponds to the data type that is present on the various
 * AirbyteMessages (e.g. AirbyteRecordMessage, AirbyteCatalog).
 *
 * This type system is realized using JSON schemas. In order to work around some of the limitations
 * of JSON schema, the newer version of the protocol defines new types in well_known_types.yaml.
 *
 * Note that the legacy version of the protocol relied on an airbyte_type property in the JSON
 * schema. This is NOT to be confused with the overall concept of an Airbyte data types, which is
 * essentially Airbyte's notion of what a record's data type is.
 *
 * TODO : Rename this file to AirbyteDataType.
 */
public class JsonSchemaType {

  public static final String TYPE = "type";
  public static final String REF = "$ref";
  public static final String FORMAT = "format";
  public static final String DATE_TIME = "date-time";
  public static final String DATE = "date";
  public static final String TIME = "time";
  public static final String TIME_WITHOUT_TIMEZONE = "time_without_timezone";
  public static final String TIME_WITH_TIMEZONE = "time_with_timezone";
  public static final String TIMESTAMP_WITH_TIMEZONE = "timestamp_with_timezone";
  public static final String TIMESTAMP_WITHOUT_TIMEZONE = "timestamp_without_timezone";
  public static final String AIRYBTE_INT_TYPE = "integer";
  public static final String CONTENT_ENCODING = "contentEncoding";
  public static final String BASE_64 = "base64";
  public static final String LEGACY_AIRBYTE_TYPE_PROPERTY = "airbyte_type";
  public static final String ITEMS = "items";

  public static final JsonSchemaType STRING_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.STRING_V1).build();
  public static final JsonSchemaType BINARY_DATA_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.BINARY_DATA_V1).build();
  public static final JsonSchemaType DATE_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.DATE_V1).build();
  public static final JsonSchemaType TIMESTAMP_WITH_TIMEZONE_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.TIMESTAMP_WITH_TIMEZONE_V1).build();
  public static final JsonSchemaType TIMESTAMP_WITHOUT_TIMEZONE_V1 =
      JsonSchemaType.builder(JsonSchemaPrimitive.TIMESTAMP_WITHOUT_TIMEZONE_V1).build();
  public static final JsonSchemaType TIME_WITH_TIMEZONE_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.TIME_WITH_TIMEZONE_V1).build();
  public static final JsonSchemaType TIME_WITHOUT_TIMEZONE_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.TIME_WITHOUT_TIMEZONE_V1).build();
  public static final JsonSchemaType NUMBER_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER_V1).build();
  public static final JsonSchemaType INTEGER_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.INTEGER_V1).build();
  public static final JsonSchemaType BOOLEAN_V1 = JsonSchemaType.builder(JsonSchemaPrimitive.BOOLEAN_V1).build();

  public static final JsonSchemaType STRING = JsonSchemaType.builder(JsonSchemaPrimitive.STRING).build();
  public static final JsonSchemaType NUMBER = JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER).build();
  public static final JsonSchemaType INTEGER =
      JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER).withLegacyAirbyteTypeProperty(AIRYBTE_INT_TYPE).build();
  public static final JsonSchemaType BOOLEAN = JsonSchemaType.builder(JsonSchemaPrimitive.BOOLEAN).build();
  public static final JsonSchemaType OBJECT = JsonSchemaType.builder(JsonSchemaPrimitive.OBJECT).build();
  public static final JsonSchemaType ARRAY = JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY).build();
  public static final JsonSchemaType NULL = JsonSchemaType.builder(JsonSchemaPrimitive.NULL).build();
  public static final JsonSchemaType STRING_BASE_64 = JsonSchemaType.builder(JsonSchemaPrimitive.STRING).withContentEncoding(BASE_64).build();
  public static final JsonSchemaType STRING_TIME_WITH_TIMEZONE =
      JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
          .withFormat(TIME)
          .withLegacyAirbyteTypeProperty(TIME_WITH_TIMEZONE).build();
  public static final JsonSchemaType STRING_TIME_WITHOUT_TIMEZONE =
      JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
          .withFormat(TIME)
          .withLegacyAirbyteTypeProperty(TIME_WITHOUT_TIMEZONE).build();
  public static final JsonSchemaType STRING_TIMESTAMP_WITH_TIMEZONE =
      JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
          .withFormat(DATE_TIME)
          .withLegacyAirbyteTypeProperty(TIMESTAMP_WITH_TIMEZONE).build();
  public static final JsonSchemaType STRING_TIMESTAMP_WITHOUT_TIMEZONE =
      JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
          .withFormat(DATE_TIME)
          .withLegacyAirbyteTypeProperty(TIMESTAMP_WITHOUT_TIMEZONE).build();
  public static final JsonSchemaType STRING_DATE =
      JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
          .withFormat(DATE)
          .build();
  public static final JsonSchemaType NUMBER_BIGINT =
      JsonSchemaType.builder(JsonSchemaPrimitive.STRING)
          .withLegacyAirbyteTypeProperty("big_integer")
          .build();

  private final Map<String, Object> jsonSchemaTypeMap;

  private JsonSchemaType(final Map<String, Object> jsonSchemaTypeMap) {
    this.jsonSchemaTypeMap = jsonSchemaTypeMap;
  }

  public static Builder builder(final JsonSchemaPrimitive type) {
    return new Builder(type);
  }

  public Map<String, Object> getJsonSchemaTypeMap() {
    return jsonSchemaTypeMap;
  }

  public static class Builder {

    private final ImmutableMap.Builder<String, Object> typeMapBuilder;

    private Builder(final JsonSchemaPrimitive type) {
      typeMapBuilder = ImmutableMap.builder();
      if (JsonSchemaPrimitiveUtil.isV0Schema(type)) {
        typeMapBuilder.put(TYPE, type.name().toLowerCase());
      } else {
        typeMapBuilder.put(REF, PRIMITIVE_TO_REFERENCE_BIMAP.get(type));
      }
    }

    public Builder withFormat(final String value) {
      typeMapBuilder.put(FORMAT, value);
      return this;
    }

    public Builder withContentEncoding(final String value) {
      typeMapBuilder.put(CONTENT_ENCODING, value);
      return this;
    }

    public Builder withLegacyAirbyteTypeProperty(final String value) {
      typeMapBuilder.put(LEGACY_AIRBYTE_TYPE_PROPERTY, value);
      return this;
    }

    public JsonSchemaType build() {
      return new JsonSchemaType(typeMapBuilder.build());
    }

    public Builder withItems(final JsonSchemaType items) {
      typeMapBuilder.put(ITEMS, items.getJsonSchemaTypeMap());
      return this;
    }

  }

  @Override
  public String toString() {
    return String.format("JsonSchemaType(%s)", jsonSchemaTypeMap.toString());
  }

  @Override
  public boolean equals(final Object other) {
    if (other == null) {
      return false;
    }
    if (!(other instanceof final JsonSchemaType that)) {
      return false;
    }
    return Objects.equals(this.jsonSchemaTypeMap, that.jsonSchemaTypeMap);
  }

  @Override
  public int hashCode() {
    return Objects.hashCode(this.jsonSchemaTypeMap);
  }

}
