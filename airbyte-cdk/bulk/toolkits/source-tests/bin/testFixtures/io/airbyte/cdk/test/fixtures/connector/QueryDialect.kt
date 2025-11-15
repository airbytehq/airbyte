/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */

package io.airbyte.cdk.test.fixtures.connector

import io.airbyte.cdk.jdbc.JdbcFieldType

interface QueryDialect {
    fun buildCreateNamespaceQuery(namespace: String): String

    fun buildCreateTableQuery(tableDefinition: TableDefinition): String

    fun buildDropNamespaceQuery(namespace: String): String

    fun buildDropTableQuery(namespace: String, tableName: String): String

    fun buildInsertQuery(tableDefinition: TableDefinition, data: Map<String, Any?>): String

    fun buildDeleteQuery(tableDefinition: TableDefinition, condition: String?): String

    fun mapColumnTypeToSql(
        type: ColumnType,
        length: Int = 0,
        precision: Int = 0,
        scale: Int = 0,
    ): String

    fun escapeIdentifier(identifier: String): String

    fun formatValue(value: Any?): String =
        when (value) {
            null -> "NULL"
            is Number -> value.toString()
            is Boolean -> if (value) "1" else "0"
            else -> "'${value.toString().replace("'", "''")}'"
        }

    fun getFullyQualifiedName(td: TableDefinition): String =
        getFullyQualifiedName(td.namespace, td.tableName)

    fun getFullyQualifiedName(namespace: String, tableName: String): String =
        "${escapeIdentifier(namespace)}.${escapeIdentifier(tableName)}"
}

data class TableDefinition(
    val namespace: String,
    val tableName: String,
    val columns: List<ColumnDefinition>,
    val tableOptions: String = "",
)

data class ColumnDefinition(
    val name: String,
    val type: ColumnType,
    val jdbcType: JdbcFieldType<*>,
    val length: Int = 0,
    val precision: Int = 0,
    val scale: Int = 0,
    val isNullable: Boolean = true,
    val isPrimaryKey: Boolean = false,
    val defaultValue: String? = null,
)

enum class ColumnType {
    INTEGER,
    BIGINT,
    VARCHAR,
    DATE,
    TIME,
    TIMESTAMP,
}
