/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

public class Field extends CommonField<JsonSchemaType> {

  private Field(final String name, final JsonSchemaType type) {
    super(name, type);
  }

  private Field(final String name, final JsonSchemaType type, final int columnSize) {
    super(name, type, columnSize);
  }

  public static Field of(final String name, final JsonSchemaType type) {
    return new Field(name, type);
  }

  public static Field of(final String name, final JsonSchemaType type, final int columnSize) {
    return new Field(name, type, columnSize);
  }

}
