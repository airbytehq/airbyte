/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.snowflake

import io.airbyte.integrations.sourceTesting.ColumnType
import io.airbyte.integrations.sourceTesting.SqlDialect
import io.airbyte.integrations.sourceTesting.TableDefinition

class SnowflakeSqlDialect : SqlDialect() {

    override fun buildCreateNamespaceQuery(namespace: String): String =
        "CREATE SCHEMA IF NOT EXISTS ${escapeIdentifier(namespace)}"

    override fun buildDropNamespaceQuery(namespace: String): String =
        "DROP SCHEMA IF EXISTS ${escapeIdentifier(namespace)} CASCADE"

    override fun buildCreateTableQuery(tableDefinition: TableDefinition): String {
        val columns =
            tableDefinition.columns.joinToString(", ") { col ->
                val nullableClause = if (col.isNullable) "" else " NOT NULL"
                val primaryKeyClause = if (col.isPrimaryKey) " PRIMARY KEY" else ""
                val defaultClause =
                    col.defaultValue?.let {
                        val defaultValue =
                            when {
                                it.equals("CURRENT_TIMESTAMP", ignoreCase = true) ->
                                    "CURRENT_TIMESTAMP()"
                                else -> it
                            }
                        " DEFAULT $defaultValue"
                    }
                        ?: ""

                "${escapeIdentifier(col.name)} ${mapColumnTypeToSql(col.type, col.length, col.precision, col.scale)}$nullableClause$primaryKeyClause$defaultClause"
            }

        return "CREATE TABLE IF NOT EXISTS ${escapeIdentifier(tableDefinition.namespace)}.${escapeIdentifier(tableDefinition.tableName)} ($columns)"
    }

    override fun mapColumnTypeToSql(
        type: ColumnType,
        length: Int,
        precision: Int,
        scale: Int,
    ): String =
        when (type) {
            ColumnType.INTEGER -> "INTEGER"
            ColumnType.BIGINT -> "BIGINT"
            ColumnType.VARCHAR -> if (length > 0) "VARCHAR($length)" else "VARCHAR(255)"
            ColumnType.DATE -> "DATE"
            ColumnType.TIME -> "TIME"
            ColumnType.TIMESTAMP -> "TIMESTAMP"
        }

    override fun escapeIdentifier(identifier: String): String {
        return "\"${identifier}\""
    }

    override fun formatValue(value: Any?): String =
        when (value) {
            null -> "NULL"
            is Number -> value.toString()
            is Boolean -> if (value) "TRUE" else "FALSE"
            else -> "'${value.toString().replace("'", "''")}'"
        }

    override fun buildDropTableQuery(namespace: String, tableName: String): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(namespace, tableName)}"
}
