package io.airbyte.integrations.source.relationaldb;

import java.sql.JDBCType;
import java.util.Objects;

class RelationalDbColumnInfo extends AbstractField<T> {

  private final String columnName;
  private final JDBCType columnType;

  public RelationalDbColumnInfo(String columnName, JDBCType columnType) {
    this.columnName = columnName;
    this.columnType = columnType;
  }

  public String getColumnName() {
    return columnName;
  }

  public JDBCType getColumnType() {
    return columnType;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    RelationalDbColumnInfo that = (RelationalDbColumnInfo) o;
    return Objects.equals(columnName, that.columnName) && columnType == that.columnType;
  }

  @Override
  public int hashCode() {
    return Objects.hash(columnName, columnType);
  }

  @Override
  public String toString() {
    return "ColumnInfo{" +
        "columnName='" + columnName + '\'' +
        ", columnType=" + columnType +
        '}';
  }

}
