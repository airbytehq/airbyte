/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import com.google.common.collect.ImmutableMap;
import java.util.Map;

public class JsonSchemaType {

  public static final String TYPE = "type";
  public static final String FORMAT = "format";
  public static final String DATE_TIME = "date-time";
  public static final String DATE = "date";
  public static final String TIME = "time";
  public static final String TIMESTAMP_WITH_TIMEZONE = "timestamp_with_timezone";
  public static final String TIMESTAMP_WITHOUT_TIMEZONE = "timestamp";
  public static final String CONTENT_ENCODING = "contentEncoding";
  public static final String BASE_64 = "base64";
  public static final String AIRBYTE_TYPE = "airbyte_type";

  public static final JsonSchemaType STRING = JsonSchemaType.builder(JsonSchemaPrimitive.STRING).build();
  public static final JsonSchemaType NUMBER = JsonSchemaType.builder(JsonSchemaPrimitive.NUMBER).build();
  public static final JsonSchemaType BOOLEAN = JsonSchemaType.builder(JsonSchemaPrimitive.BOOLEAN).build();
  public static final JsonSchemaType OBJECT = JsonSchemaType.builder(JsonSchemaPrimitive.OBJECT).build();
  public static final JsonSchemaType ARRAY = JsonSchemaType.builder(JsonSchemaPrimitive.ARRAY).build();
  public static final JsonSchemaType NULL = JsonSchemaType.builder(JsonSchemaPrimitive.NULL).build();
  public static final JsonSchemaType STRING_BASE_64 = JsonSchemaType.builder(JsonSchemaPrimitive.STRING).withContentEncoding(BASE_64).build();

  private final Map<String, String> jsonSchemaTypeMap;

  private JsonSchemaType(final Map<String, String> jsonSchemaTypeMap) {
    this.jsonSchemaTypeMap = jsonSchemaTypeMap;
  }

  public static Builder builder(final JsonSchemaPrimitive type) {
    return new Builder(type);
  }

  public Map<String, String> getJsonSchemaTypeMap() {
    return jsonSchemaTypeMap;
  }

  public static class Builder {

    private final ImmutableMap.Builder<String, String> typeMapBuilder;

    private Builder(final JsonSchemaPrimitive type) {
      typeMapBuilder = ImmutableMap.builder();
      typeMapBuilder.put(TYPE, type.name().toLowerCase());
    }

    public Builder withFormat(String value) {
      typeMapBuilder.put(FORMAT, value);
      return this;
    }

    public Builder withContentEncoding(String value) {
      typeMapBuilder.put(CONTENT_ENCODING, value);
      return this;
    }

    public Builder withAirbyteType(String value) {
      typeMapBuilder.put(AIRBYTE_TYPE, value);
      return this;
    }

    public JsonSchemaType build() {
      return new JsonSchemaType(typeMapBuilder.build());
    }

  }

}
