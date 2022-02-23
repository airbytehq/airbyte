/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

public class Field extends CommonField<JsonSchemaPrimitive> {

  public Field(final String name, final JsonSchemaPrimitive type) {
    super(name, type);
  }

  public static Field of(final String name, final JsonSchemaPrimitive type) {
    return new Field(name, type);
  }

  public String getTypeAsJsonSchemaString() {
    return getType().name().toLowerCase();
  }

}
