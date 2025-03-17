/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.netsuite

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
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
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.WhereClauseLeafNode
import io.airbyte.cdk.read.WhereClauseNode
import io.airbyte.cdk.read.WhereNode
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class NetsuiteSourceOperations() :
    JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {
    private val log = KotlinLogging.logger {}

    override val globalCursor: MetaField? = null

    override val globalMetaFields: Set<MetaField> = emptySet()

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> {
                when (type.typeName) {
                    "WLONGVARCHAR",
                    "WVARCHAR",
                    "WCHAR",
                    "LONGVARCHAR",
                    "CHAR",
                    "VARCHAR",
                    "VARCHAR2", -> StringFieldType
                    "TINYINT",
                    "BIT", -> BooleanFieldType
                    "BIGINT", -> BigIntegerFieldType
                    "BINARY",
                    "VARBINARY",
                    "LONGVARBINARY", -> BytesFieldType
                    "NUMERIC",
                    "DECIMAL", -> BigDecimalFieldType
                    "INTEGER",
                    "SMALLINT", -> BigIntegerFieldType
                    "REAL", -> BigDecimalFieldType
                    "DOUBLE", -> DoubleFieldType
                    "DATE",
                    "TIME",
                    "TIMESTAMP", -> LocalDateTimeFieldType
                    "NULL", -> PokemonFieldType // Why are we here?
                    else -> PokemonFieldType
                }
            }
            else -> PokemonFieldType
        }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> =
            listOf(
                sql(
                    select,
                    when (from) {
                        is FromSample -> Limit((from as FromSample).sampleSize.toLong())
                        else -> limit
                    }
                ),
                from.sql(),
                where.sql(),
                orderBy.sql()
            )
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

    fun Field.sql(): String = "\"$id\""

    fun FromNode.sql(): String =
        when (this) {
            is NoFrom -> "FROM DUMMY"
            is From ->
                if (this.namespace == null) "FROM \"$name\"" else "FROM \"$namespace\".\"$name\""
            is FromSample -> {
                From(name, namespace).sql()
            }
        }

    fun WhereNode.sql(): String =
        when (this) {
            is NoWhere -> ""
            is Where -> {
                "WHERE ${clause.sql()}"
            }
        }

    val format = "YYYY-MM-DD HH24:MI:SSxFF"
    fun WhereClauseNode.sql(): String =
        when (this) {
            is And -> conj.joinToString(") AND (", "(", ")") { it.sql() }
            is Or -> disj.joinToString(") OR (", "(", ")") { it.sql() }
            is Equal -> {
                when (column.type) {
                    is LocalDateTimeFieldType -> "${column.sql()} = TO_TIMESTAMP(?, '$format')"
                    else -> "${column.sql()} = ?"
                }
            }
            is GreaterOrEqual -> {
                when (column.type) {
                    is LocalDateTimeFieldType -> "${column.sql()} >= TO_TIMESTAMP(?, '$format')"
                    else -> "${column.sql()} >= ?"
                }
            }
            is Greater -> {
                when (column.type) {
                    is LocalDateTimeFieldType -> "${column.sql()} > TO_TIMESTAMP(?, '$format')"
                    else -> "${column.sql()} > ?"
                }
            }
            is LesserOrEqual -> {
                when (column.type) {
                    is LocalDateTimeFieldType -> "${column.sql()} <= TO_TIMESTAMP(?, '$format')"
                    else -> "${column.sql()} <= ?"
                }
            }
            is Lesser -> {
                when (column.type) {
                    is LocalDateTimeFieldType -> "${column.sql()} < TO_TIMESTAMP(?, '$format')"
                    else -> "${column.sql()} < ?"
                }
            }
        }

    fun OrderByNode.sql(): String =
        when (this) {
            NoOrderBy -> ""
            is OrderBy -> "ORDER BY " + columns.joinToString(", ") { it.sql() }
        }

    fun SelectQuerySpec.bindings(): List<SelectQuery.Binding> = where.bindings()

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
                log.info { "*** column: ${column.id} ${column.type} $bindingValue" }
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

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        return
    }
}
