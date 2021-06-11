package io.airbyte.protocol.models;

import java.util.Objects;

public abstract class AbstractField<T> {

  private final String name;
  private final T type;

  public AbstractField(String name, T type) {
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

    AbstractField<T> field = (AbstractField<T>) o;
    return name.equals(field.name) &&
        type == field.type;
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, type);
  }
}
