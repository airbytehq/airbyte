/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.source.select

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.source.TableName
import io.airbyte.cdk.source.Field

/**
 * Source-database-agnostic representation of a SELECT query as an abstract syntax tree.
 * This is tailored to the subset of queries that we actually might run in a source connector.
 *
 * See also [optimize] which does a pass to improve the AST.
 * See also [SelectQueryGenerator] which acts as the "compiler backend" to generate the actual SQL.
 */
data class SelectQuerySpec(
    val select: SelectNode,
    val from: FromNode = NoFrom,
    val where: WhereNode = NoWhere,
    val orderBy: OrderByNode = NoOrderBy,
    val limit: LimitNode = NoLimit,
)

sealed interface SelectNode {
    val columns: List<Field>
}

data class SelectColumns(override val columns: List<Field>) : SelectNode

data class SelectColumnMaxValue(val column: Field) : SelectNode {
    override val columns: List<Field>
        get() = listOf(column)
}

sealed interface FromNode

data object NoFrom : FromNode

data class From(val table: TableName) : FromNode

sealed interface WhereNode

data object NoWhere : WhereNode

data class Where(val clause: WhereClauseNode) : WhereNode

sealed interface WhereClauseNode

data class And(val conj: List<WhereClauseNode>) : WhereClauseNode

data class Or(val disj: List<WhereClauseNode>) : WhereClauseNode

sealed interface WhereClauseLeafNode : WhereClauseNode {
    val column: Field
    val bindingValue: JsonNode
}

data class Greater(
    override val column: Field,
    override val bindingValue: JsonNode,
) : WhereClauseLeafNode

data class LesserOrEqual(
    override val column: Field,
    override val bindingValue: JsonNode,
) : WhereClauseLeafNode

data class Equal(
    override val column: Field,
    override val bindingValue: JsonNode,
) : WhereClauseLeafNode

sealed interface OrderByNode

data class OrderBy(val columns: List<Field>) : OrderByNode

data object NoOrderBy : OrderByNode

sealed interface LimitNode

data class Limit(val n: Long) : LimitNode

data object NoLimit : LimitNode

fun SelectQuerySpec.optimize(): SelectQuerySpec =
    SelectQuerySpec(select.optimize(), from, where.optimize(), orderBy.optimize(), limit)

fun SelectNode.optimize(): SelectNode =
    when (this) {
        is SelectColumns -> SelectColumns(this.columns.distinct())
        is SelectColumnMaxValue -> this
    }

fun WhereNode.optimize(): WhereNode =
    when (this) {
        NoWhere -> this
        is Where -> Where(clause.optimize())
    }

fun WhereClauseNode.optimize(): WhereClauseNode =
    when (this) {
        is WhereClauseLeafNode -> this
        is And -> {
            val optimizedConj: List<WhereClauseNode> =
                conj.flatMap {
                    when (val optimized: WhereClauseNode = it.optimize()) {
                        is And -> optimized.conj
                        is Or -> if (optimized.disj.isEmpty()) listOf() else listOf(optimized)
                        else -> listOf(optimized)
                    }
                }
            if (optimizedConj.size == 1) {
                optimizedConj.first()
            } else {
                And(optimizedConj)
            }
        }
        is Or -> {
            val optimizedDisj: List<WhereClauseNode> =
                disj.flatMap {
                    when (val optimized: WhereClauseNode = it.optimize()) {
                        is Or -> optimized.disj
                        is And -> if (optimized.conj.isEmpty()) listOf() else listOf(optimized)
                        else -> listOf(optimized)
                    }
                }
            if (optimizedDisj.size == 1) {
                optimizedDisj.first()
            } else {
                Or(optimizedDisj)
            }
        }
    }

fun OrderByNode.optimize(): OrderByNode =
    when (this) {
        NoOrderBy -> this
        is OrderBy -> if (columns.isEmpty()) NoOrderBy else this
    }
