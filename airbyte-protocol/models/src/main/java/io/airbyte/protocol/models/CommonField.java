/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import java.util.Objects;
import java.util.Optional;

public class CommonField<T> {

  private final String name;
  private final T type;

  // the COLUMN_SIZE returned from the JDBC getColumns query
  // see https://docs.oracle.com/javase/8/docs/api/java/sql/DatabaseMetaData.html
  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  private final Optional<Integer> columnSize;

  public CommonField(final String name, final T type) {
    this.name = name;
    this.type = type;
    this.columnSize = Optional.empty();
  }

  public CommonField(final String name, final T type, final int columnSize) {
    this.name = name;
    this.type = type;
    if (columnSize <= 0) {
      this.columnSize = Optional.empty();
    } else {
      this.columnSize = Optional.of(columnSize);
    }
  }

  public String getName() {
    return name;
  }

  public T getType() {
    return type;
  }

  public Optional<Integer> getColumnSize() {
    return columnSize;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }

    final CommonField<T> field = (CommonField<T>) o;
    return name.equals(field.name) &&
        type == field.type &&
        columnSize.equals(field.columnSize);
  }

  @Override
  public int hashCode() {
    return Objects.hash(name, type, columnSize);
  }

}
