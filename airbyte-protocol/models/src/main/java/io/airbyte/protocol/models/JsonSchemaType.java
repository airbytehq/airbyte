/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import java.util.HashMap;

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

  public static final JsonSchemaType STRING = new JsonSchemaType.Builder().withType(JsonSchemaPrimitive.STRING).build();
  public static final JsonSchemaType NUMBER = new JsonSchemaType.Builder().withType(JsonSchemaPrimitive.NUMBER).build();
  public static final JsonSchemaType BOOLEAN = new JsonSchemaType.Builder().withType(JsonSchemaPrimitive.BOOLEAN).build();
  public static final JsonSchemaType OBJECT = new JsonSchemaType.Builder().withType(JsonSchemaPrimitive.OBJECT).build();
  public static final JsonSchemaType ARRAY = new JsonSchemaType.Builder().withType(JsonSchemaPrimitive.ARRAY).build();
  public static final JsonSchemaType NULL = new JsonSchemaType.Builder().withType(JsonSchemaPrimitive.NULL).build();
  public static final JsonSchemaType STRING_BASE_64 = new JsonSchemaType.Builder().withType(JsonSchemaPrimitive.STRING).withContentEncoding(BASE_64).build();

  private final HashMap<String, String> jsonSchemaTypeMap = new HashMap<>();

  public HashMap<String, String> getJsonSchemaTypeMap() {
    return jsonSchemaTypeMap;
  }

  public static class Builder {

    private final JsonSchemaType jsonSchemaType;

    public Builder() {
      jsonSchemaType = new JsonSchemaType();
    }

    public Builder withType(JsonSchemaPrimitive primitive) {
      jsonSchemaType.jsonSchemaTypeMap.put(TYPE, primitive.name().toLowerCase());
      return this;
    }

    public Builder withFormat(String value) {
      jsonSchemaType.jsonSchemaTypeMap.put(FORMAT, value);
      return this;
    }

    public Builder withContentEncoding(String value) {
      jsonSchemaType.jsonSchemaTypeMap.put(CONTENT_ENCODING, value);
      return this;
    }

    public Builder withAirbyteType(String value) {
      jsonSchemaType.jsonSchemaTypeMap.put(AIRBYTE_TYPE, value);
      return this;
    }

    public JsonSchemaType build() {
      return jsonSchemaType;
    }

  }

}
