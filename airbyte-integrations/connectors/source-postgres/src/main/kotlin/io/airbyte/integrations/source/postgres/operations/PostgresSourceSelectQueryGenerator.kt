/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations

import io.airbyte.cdk.discover.DataField
import io.airbyte.cdk.discover.NonEmittedField
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.Equal
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.FromNode
import io.airbyte.cdk.read.FromSample
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.GreaterOrEqual
import io.airbyte.cdk.read.Lesser
import io.airbyte.cdk.read.LesserOrEqual
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.LimitNode
import io.airbyte.cdk.read.NoFrom
import io.airbyte.cdk.read.NoLimit
import io.airbyte.cdk.read.NoOrderBy
import io.airbyte.cdk.read.NoWhere
import io.airbyte.cdk.read.Or
import io.airbyte.cdk.read.OrderBy
import io.airbyte.cdk.read.OrderByNode
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectNode
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.WhereClauseLeafNode
import io.airbyte.cdk.read.WhereClauseNode
import io.airbyte.cdk.read.WhereNode
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class PostgresSourceSelectQueryGenerator : SelectQueryGenerator {

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> =
            listOf(select.sql(), from.sql(/*select.columns*/), where.sql(), orderBy.sql())
        val sqlWithoutLimit: String = components.filter { it.isNotBlank() }.joinToString(" ")
        val limitClause: String =
            when (limit) {
                NoLimit -> return sqlWithoutLimit
                Limit(0) -> "LIMIT 0"
                is Limit -> "LIMIT ?"
            }
        return if (where == NoWhere && orderBy == NoOrderBy) {
            "$sqlWithoutLimit $limitClause"
        } else {
            "${select.sql()} FROM ($sqlWithoutLimit) $limitClause"
        }
    }

    fun SelectNode.sql(): String =
        "SELECT " +
            when (this) {
                is SelectColumns -> columns.joinToString(", ") { it.sql() }
                is SelectColumnMaxValue -> "MAX(${column.sql()})"
            }

    /*fun Field.sql(): String = when(id) {
        "ctid" -> "ctid::text"
        else -> "\"$id\""
    }*/

    fun DataField.sql(): String = "\"$id\""

    fun FromNode.sql(
        /*columns: List<DataField>,*/
    ): String =
        when (this) {
            NoFrom -> "FROM DUAL"
            is From ->
                if (this.namespace == null) "FROM \"$name\"" else "FROM \"$namespace\".\"$name\""
            /*is FromSample -> {
                val sample: String =
                    if (sampleRateInv == 1L) {
                        ""
                    } else {
                        " TABLESAMPLE SYSTEM(GREATEST(${sampleRatePercentage.toPlainString()}, 0.001))"
                    }
                val whereSample = where?.let { " ${it.sql()}" } ?: ""

                val innerFrom: String = From(name, namespace).sql(columns) + sample + whereSample
                val inner =
                    "SELECT ${columns.joinToString(", ") { it.sql() }} $innerFrom ORDER BY RANDOM()"
                "FROM (SELECT ${columns.joinToString(", ") { it.sql() }} FROM ($inner) AS ts LIMIT $sampleSize) AS l"
            }*/
            is FromSample -> From(name, namespace).sql()
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
            is Equal ->
                when (column) {
                    is NonEmittedField -> "${column.sql()} = ?::tid"
                    else -> "${column.sql()} = ?"
                }
            is GreaterOrEqual ->
                when (column) {
                    is NonEmittedField -> "${column.sql()} >= ?::tid"
                    else -> "${column.sql()} >= ?"
                }
            is Greater ->
                when (column) {
                    is NonEmittedField -> "${column.sql()} > ?::tid"
                    else -> "${column.sql()} > ?"
                }
            is LesserOrEqual ->
                when (column) {
                    is NonEmittedField -> "${column.sql()} <= ?::tid"
                    else -> "${column.sql()} <= ?"
                }
            is Lesser ->
                when (column) {
                    is NonEmittedField -> "${column.sql()} < ?::tid"
                    else -> "${column.sql()} < ?"
                }
        }

    fun OrderByNode.sql(): String =
        when (this) {
            NoOrderBy -> ""
            is OrderBy -> "ORDER BY " + columns.joinToString(", ") { it.sql() }
        }

    fun SelectQuerySpec.bindings(): List<SelectQuery.Binding> =
        from.bindings() + where.bindings() + limit.bindings()

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
            Limit(0) -> listOf()
            is Limit -> listOf(SelectQuery.Binding(Jsons.numberNode(n), LongFieldType))
        }

    fun FromNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            is NoFrom,
            is From -> listOf()
            is FromSample -> this.where?.let { it.bindings() } ?: listOf()
        }
}
