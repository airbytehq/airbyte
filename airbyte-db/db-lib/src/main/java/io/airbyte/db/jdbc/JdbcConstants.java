/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

public final class JdbcConstants {

  // constants defined in the DatabaseMetaData#getColumns method
  // reference: https://docs.oracle.com/javase/8/docs/api/java/sql/DatabaseMetaData.html
  public static final String JDBC_COLUMN_DATABASE_NAME = "TABLE_CAT";
  public static final String JDBC_COLUMN_SCHEMA_NAME = "TABLE_SCHEM";
  public static final String JDBC_COLUMN_TABLE_NAME = "TABLE_NAME";
  public static final String JDBC_COLUMN_COLUMN_NAME = "COLUMN_NAME";
  public static final String JDBC_COLUMN_DATA_TYPE = "DATA_TYPE";
  public static final String JDBC_COLUMN_TYPE_NAME = "TYPE_NAME";
  public static final String JDBC_COLUMN_SIZE = "COLUMN_SIZE";
  public static final String JDBC_IS_NULLABLE = "IS_NULLABLE";

  public static final String INTERNAL_SCHEMA_NAME = "schemaName";
  public static final String INTERNAL_TABLE_NAME = "tableName";
  public static final String INTERNAL_COLUMN_NAME = "columnName";
  public static final String INTERNAL_COLUMN_TYPE = "columnType";
  public static final String INTERNAL_COLUMN_TYPE_NAME = "columnTypeName";
  public static final String INTERNAL_COLUMN_SIZE = "columnSize";
  public static final String INTERNAL_IS_NULLABLE = "isNullable";

}
