/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import com.google.common.collect.ImmutableMap;

public enum JsonSchemaPrimitive {

  STRING_BINARY(ImmutableMap.of("type", "string", "contentEncoding", "base64")),
  STRING(ImmutableMap.of("type", "string")),
  NUMBER(ImmutableMap.of("type", "number")),
  OBJECT(ImmutableMap.of("type", "object")),
  ARRAY(ImmutableMap.of("type", "array")),
  BOOLEAN(ImmutableMap.of("type", "boolean")),
  NULL(ImmutableMap.of("type", "null"));

  private final ImmutableMap<String, String> jsonSchemaTypeMap;

  JsonSchemaPrimitive(ImmutableMap<String, String> jsonSchemaTypeMap) {
    this.jsonSchemaTypeMap = jsonSchemaTypeMap;
  }

  public ImmutableMap<String, String> getJsonSchemaTypeMap() {
    return jsonSchemaTypeMap;
  }

}
