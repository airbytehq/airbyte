/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import java.util.Objects;

public class CommonField<T> {

  private final String name;
  private final T type;

  public CommonField(String name, T type) {
    this.name = name;
    this.type = type;
  }

  public String getName() {
    return name;
  }

  public T getType() {
    return type;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }

    CommonField<T> field = (CommonField<T>) o;
    return name.equals(field.name) &&
        type == field.type;
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, type);
  }

}
