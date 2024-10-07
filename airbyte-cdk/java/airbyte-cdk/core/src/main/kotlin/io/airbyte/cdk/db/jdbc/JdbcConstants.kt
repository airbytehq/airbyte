/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

object JdbcConstants {
    // constants defined in the DatabaseMetaData#getColumns method
    // reference: https://docs.oracle.com/javase/8/docs/api/java/sql/DatabaseMetaData.html
    const val JDBC_COLUMN_DATABASE_NAME: String = "TABLE_CAT"
    const val JDBC_COLUMN_SCHEMA_NAME: String = "TABLE_SCHEM"
    const val JDBC_COLUMN_TABLE_NAME: String = "TABLE_NAME"
    const val JDBC_COLUMN_COLUMN_NAME: String = "COLUMN_NAME"
    const val JDBC_COLUMN_DATA_TYPE: String = "DATA_TYPE"
    const val JDBC_COLUMN_TYPE: String = "TYPE"

    const val JDBC_COLUMN_TYPE_NAME: String = "TYPE_NAME"
    const val JDBC_COLUMN_SIZE: String = "COLUMN_SIZE"
    const val JDBC_INDEX_NAME: String = "INDEX_NAME"
    const val JDBC_IS_NULLABLE: String = "IS_NULLABLE"
    const val JDBC_DECIMAL_DIGITS: String = "DECIMAL_DIGITS"
    const val JDBC_INDEX_NON_UNIQUE: String = "NON_UNIQUE"
    const val INTERNAL_SCHEMA_NAME: String = "schemaName"
    const val INTERNAL_TABLE_NAME: String = "tableName"
    const val INTERNAL_COLUMN_NAME: String = "columnName"
    const val INTERNAL_COLUMN_TYPE: String = "columnType"
    const val INTERNAL_COLUMN_TYPE_NAME: String = "columnTypeName"
    const val INTERNAL_COLUMN_SIZE: String = "columnSize"
    const val INTERNAL_IS_NULLABLE: String = "isNullable"
    const val INTERNAL_DECIMAL_DIGITS: String = "decimalDigits"
    const val KEY_SEQ: String = "KEY_SEQ"
}
