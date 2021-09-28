/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import java.util.Objects;

public class SchemaTableNamePair {

  public String schemaName;
  public String tableName;

  public SchemaTableNamePair(String schemaName, String tableName) {
    this.schemaName = schemaName;
    this.tableName = tableName;
  }

  @Override
  public String toString() {
    return "SchemaTableNamePair{" +
        "schemaName='" + schemaName + '\'' +
        ", tableName='" + tableName + '\'' +
        '}';
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    SchemaTableNamePair that = (SchemaTableNamePair) o;
    return Objects.equals(schemaName, that.schemaName) && Objects.equals(tableName, that.tableName);
  }

  @Override
  public int hashCode() {
    return Objects.hash(schemaName, tableName);
  }

  public String getFullyQualifiedTableName() {
    return schemaName + "." + tableName;
  }

}
