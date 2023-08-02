/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import com.google.common.collect.ImmutableSet;
import java.util.Comparator;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeSet;

public class TableSchema {

  private final SortedSet<ColumnMetadata> columns;

  public TableSchema() {
    columns = new TreeSet<>(Comparator.comparingInt(ColumnMetadata::position));
  }

  public void addColumn(ColumnMetadata columnMetadata) {
    columns.add(columnMetadata);
  }

  public Set<ColumnMetadata> columns() {
    return ImmutableSet.copyOf(columns);
  }

}
