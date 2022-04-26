/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

public class Field extends CommonField<JsonSchemaType> {

  public Field(final String name, final JsonSchemaType type) {
    super(name, type);
  }

  public static Field of(final String name, final JsonSchemaType type) {
    return new Field(name, type);
  }

}
