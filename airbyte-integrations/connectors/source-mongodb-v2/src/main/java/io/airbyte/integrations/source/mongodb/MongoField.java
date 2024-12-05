/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.util.Objects;

/**
 * Custom implementation of {@link Field} that only uses the name of the field for equality. This is
 * to support MongoDB's unstructured documents which may contain more than one document with the
 * same field name, but different data type.
 */
public class MongoField extends Field {

  public MongoField(final String name, final JsonSchemaType type) {
    super(name, type);
  }

  public boolean equals(Object o) {
    if (this == o) {
      return true;
    } else if (o != null && this.getClass() == o.getClass()) {
      final MongoField field = (MongoField) o;
      return this.getName().equals(field.getName());
    } else {
      return false;
    }
  }

  public int hashCode() {
    return Objects.hash(this.getName());
  }

}
