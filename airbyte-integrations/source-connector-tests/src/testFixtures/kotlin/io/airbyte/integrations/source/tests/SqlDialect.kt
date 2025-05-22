/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tests

import io.airbyte.cdk.jdbc.JdbcFieldType

interface SqlDialect {
    fun buildCreateNamespaceQuery(namespace: String): String

    fun buildCreateTableQuery(tableDefinition: TableDefinition): String

    fun buildDropNamespaceQuery(namespace: String): String

    fun buildDropTableQuery(
        namespace: String,
        tableName: String,
    ): String

    fun buildInsertQuery(
        tableDefinition: TableDefinition,
        data: Map<String, Any?>,
    ): String

    fun buildDeleteQuery(
        tableDefinition: TableDefinition,
        condition: String?,
    ): String

    fun mapColumnTypeToSql(
        type: ColumnType,
        length: Int = 0,
        precision: Int = 0,
        scale: Int = 0,
    ): String

    fun escapeIdentifier(identifier: String): String

    fun formatValue(value: Any?): String

    /**
     * Builds a query to find all tables in the database matching a pattern. This is used for
     * cleanup operations to identify test-generated tables. Implementation is database-specific.
     * For tables we want to filter by namespace and table name both.
     */
    fun buildFindAllTablesQuery(): String =
        throw UnsupportedOperationException("Table query not implemented for this dialect")

    /**
     * Builds a query to find all namespaces/schemas in the database matching a pattern. This is
     * used for cleanup operations to identify test-generated namespaces. Implementation is
     * database-specific.
     */
    fun buildFindAllNamespacesQuery(): String =
        throw UnsupportedOperationException(
            "Namespace query not implemented for this dialect",
        )

    // Name of the column in the metadata table that contains the namespace/schema name.
    fun getNamespaceMetaFieldName(): String =
        throw UnsupportedOperationException(
            "Namespace meta field name not defined for this dialect"
        )

    // Name of the column in the metadata table that contains the table name.
    fun getTableMetaFieldName(): String =
        throw UnsupportedOperationException("Table meta field name not defined for this dialect")
}

abstract class BaseSqlDialect : SqlDialect {

    override fun buildInsertQuery(
        tableDefinition: TableDefinition,
        data: Map<String, Any?>,
    ): String {
        val columns = data.keys.joinToString(", ") { escapeIdentifier(it) }
        val values = data.values.joinToString(", ") { formatValue(it) }

        return "INSERT INTO ${escapeIdentifier(
            tableDefinition.namespace,
        )}.${escapeIdentifier(tableDefinition.tableName)} ($columns) VALUES ($values)"
    }

    override fun buildDeleteQuery(
        tableDefinition: TableDefinition,
        condition: String?,
    ): String {
        val whereClause = condition?.let { "WHERE $it" } ?: ""
        return "DELETE FROM ${escapeIdentifier(
            tableDefinition.namespace,
        )}.${escapeIdentifier(tableDefinition.tableName)} $whereClause"
    }

    override fun formatValue(value: Any?): String =
        when (value) {
            null -> "NULL"
            is String -> "'${value.replace("'", "''")}'"
            is Number -> value.toString()
            is Boolean -> if (value) "1" else "0"
            else -> "'${value.toString().replace("'", "''")}'"
        }
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
