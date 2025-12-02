/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.test.fixtures.connector

abstract class SqlDialect : QueryDialect {

    override fun buildDropTableQuery(
        namespace: String,
        tableName: String,
    ): String = "DROP TABLE ${getFullyQualifiedName(namespace, tableName)}"

    override fun buildInsertQuery(
        tableDefinition: TableDefinition,
        data: Map<String, Any?>,
    ): String {
        val columns = data.keys.joinToString(", ") { escapeIdentifier(it) }
        val values = data.values.joinToString(", ") { formatValue(it) }

        return "INSERT INTO ${getFullyQualifiedName(tableDefinition)} ($columns) VALUES ($values)"
    }

    override fun buildDeleteQuery(
        tableDefinition: TableDefinition,
        condition: String?,
    ): String {
        val whereClause = condition?.let { "WHERE $it" } ?: ""
        return "DELETE FROM ${getFullyQualifiedName(tableDefinition)} $whereClause"
    }

    override fun buildCreateNamespaceQuery(namespace: String): String = "CREATE SCHEMA $namespace"

    override fun buildDropNamespaceQuery(namespace: String): String = "DROP SCHEMA $namespace"

    override fun formatValue(value: Any?): String =
        when (value) {
            null -> "NULL"
            is Number -> value.toString()
            is Boolean -> if (value) "1" else "0"
            else -> "'${value.toString().replace("'", "''")}'"
        }

    override fun getFullyQualifiedName(td: TableDefinition): String =
        getFullyQualifiedName(td.namespace, td.tableName)

    override fun getFullyQualifiedName(namespace: String, tableName: String): String =
        "${escapeIdentifier(namespace)}.${escapeIdentifier(tableName)}"
}
