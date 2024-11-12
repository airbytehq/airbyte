/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.read.*
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class MsSqlServerSelectQueryGenerator : SelectQueryGenerator {
    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> =
            listOf(sql(select, limit), from.sql(), where.sql(), orderBy.sql())
        val sql: String = components.filter { it.isNotBlank() }.joinToString(" ")
        return sql
    }

    fun sql(selectNode: SelectNode, limit: LimitNode): String {
        val topClause: String =
            when (limit) {
                NoLimit -> ""
                Limit(0) -> "TOP 0 "
                is Limit -> "TOP ${limit.n} "
            }
        return "SELECT $topClause" +
            when (selectNode) {
                is SelectColumns -> selectNode.columns.joinToString(", ") { it.sql() }
                is SelectColumnMaxValue -> "MAX(${selectNode.column.sql()})"
            }
    }

    fun Field.sql(): String = "$id"

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> ""
            is From -> if (this.namespace == null) "FROM $name" else "FROM $namespace.$name"
            is FromSample -> {
                val from: String = From(name, namespace).sql()
                // On a table that is very big we limit sampling to no less than 0.05%
                // chance of a row getting picked. This comes at a price of bias to the beginning
                // of table on very large tables ( > 100s million of rows)
                val greatestRate: String = 0.00005.toString()
                // Quick approximation to "select count(*) from table" which doesn't require
                // full table scan.
                val quickCount =
                    "SELECT table_rows FROM information_schema.tables WHERE table_schema = '$namespace' AND table_name = '$name'"
                val greatest = "GREATEST($greatestRate, $sampleSize / ($quickCount))"
                // Rand returns a value between 0 and 1
                val where = "WHERE RAND() < $greatest "
                "$from $where"
            }
        }

    fun WhereNode.sql(): String =
        when (this) {
            NoWhere -> ""
            is Where -> "WHERE ${clause.sql()}"
        }

    fun WhereClauseNode.sql(): String =
        when (this) {
            is And -> conj.joinToString(") AND (", "(", ")") { it.sql() }
            is Or -> disj.joinToString(") OR (", "(", ")") { it.sql() }
            is Equal -> "${column.sql()} = ?"
            is Greater -> "${column.sql()} > ?"
            is GreaterOrEqual -> "${column.sql()} >= ?"
            is LesserOrEqual -> "${column.sql()} <= ?"
            is Lesser -> "${column.sql()} < ?"
        }

    fun OrderByNode.sql(): String =
        when (this) {
            NoOrderBy -> ""
            is OrderBy -> "ORDER BY " + columns.joinToString(", ") { it.sql() }
        }

    fun SelectQuerySpec.bindings(): List<SelectQuery.Binding> = where.bindings() + limit.bindings()

    fun WhereNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            is NoWhere -> listOf()
            is Where -> clause.bindings()
        }

    fun WhereClauseNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            is And -> conj.flatMap { it.bindings() }
            is Or -> disj.flatMap { it.bindings() }
            is WhereClauseLeafNode -> {
                val type = column.type as LosslessJdbcFieldType<*, *>
                listOf(SelectQuery.Binding(bindingValue, type))
            }
        }

    fun LimitNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            NoLimit,
            Limit(0),
            is Limit -> emptyList()
        }
}
