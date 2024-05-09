/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.source

import io.airbyte.cdk.source.ArrayFieldType
import io.airbyte.cdk.source.BigDecimalFieldType
import io.airbyte.cdk.source.BigIntegerFieldType
import io.airbyte.cdk.source.BinaryStreamFieldType
import io.airbyte.cdk.source.BooleanFieldType
import io.airbyte.cdk.source.ByteFieldType
import io.airbyte.cdk.source.BytesFieldType
import io.airbyte.cdk.source.ClobFieldType
import io.airbyte.cdk.source.DoubleFieldType
import io.airbyte.cdk.source.FloatFieldType
import io.airbyte.cdk.source.IntFieldType
import io.airbyte.cdk.source.LocalDateTimeFieldType
import io.airbyte.cdk.source.LocalDateFieldType
import io.airbyte.cdk.source.LocalTimeFieldType
import io.airbyte.cdk.source.NClobFieldType
import io.airbyte.cdk.source.NStringFieldType
import io.airbyte.cdk.source.OffsetDateTimeFieldType
import io.airbyte.cdk.source.OffsetTimeFieldType
import io.airbyte.cdk.source.NullFieldType
import io.airbyte.cdk.source.LosslessFieldType
import io.airbyte.cdk.source.ShortFieldType
import io.airbyte.cdk.source.StringFieldType
import io.airbyte.cdk.source.TableName
import io.airbyte.cdk.source.UrlFieldType
import io.airbyte.cdk.source.FieldType
import io.airbyte.cdk.source.PokemonFieldType
import io.airbyte.cdk.source.XmlFieldType
import io.airbyte.cdk.jdbc.JdbcMetadataQuerier
import io.airbyte.cdk.source.select.And
import io.airbyte.cdk.source.select.Equal
import io.airbyte.cdk.source.select.From
import io.airbyte.cdk.source.select.FromNode
import io.airbyte.cdk.source.select.Greater
import io.airbyte.cdk.source.select.LesserOrEqual
import io.airbyte.cdk.source.select.Limit
import io.airbyte.cdk.source.select.LimitNode
import io.airbyte.cdk.source.select.NoFrom
import io.airbyte.cdk.source.select.NoLimit
import io.airbyte.cdk.source.select.NoOrderBy
import io.airbyte.cdk.source.select.NoWhere
import io.airbyte.cdk.source.select.Or
import io.airbyte.cdk.source.select.OrderBy
import io.airbyte.cdk.source.select.OrderByNode
import io.airbyte.cdk.source.select.SelectColumnMaxValue
import io.airbyte.cdk.source.select.SelectColumns
import io.airbyte.cdk.source.select.SelectNode
import io.airbyte.cdk.source.select.SelectQuery
import io.airbyte.cdk.source.select.SelectQueryGenerator
import io.airbyte.cdk.source.select.SelectQuerySpec
import io.airbyte.cdk.source.select.Where
import io.airbyte.cdk.source.select.WhereClauseLeafNode
import io.airbyte.cdk.source.select.WhereClauseNode
import io.airbyte.cdk.source.select.WhereNode
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.sql.JDBCType

/** Stateless connector-specific logic for [TestSource]. */
@Singleton
@Requires(env = [Environment.TEST])
@Secondary
class TestSourceOperations : JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator {

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (c.type.jdbcType) {
            JDBCType.BIT,
            JDBCType.BOOLEAN -> BooleanFieldType
            JDBCType.TINYINT -> ByteFieldType
            JDBCType.SMALLINT -> ShortFieldType
            JDBCType.INTEGER -> IntFieldType
            JDBCType.BIGINT -> BigIntegerFieldType
            JDBCType.FLOAT -> FloatFieldType
            JDBCType.DOUBLE -> DoubleFieldType
            JDBCType.REAL,
            JDBCType.NUMERIC,
            JDBCType.DECIMAL -> BigDecimalFieldType
            JDBCType.CHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR -> StringFieldType
            JDBCType.NCHAR,
            JDBCType.NVARCHAR,
            JDBCType.LONGNVARCHAR -> NStringFieldType
            JDBCType.DATE -> LocalDateFieldType
            JDBCType.TIME -> LocalTimeFieldType
            JDBCType.TIMESTAMP -> LocalDateTimeFieldType
            JDBCType.TIME_WITH_TIMEZONE -> OffsetTimeFieldType
            JDBCType.TIMESTAMP_WITH_TIMEZONE -> OffsetDateTimeFieldType
            JDBCType.BLOB -> BinaryStreamFieldType
            JDBCType.BINARY,
            JDBCType.VARBINARY,
            JDBCType.LONGVARBINARY -> BytesFieldType
            JDBCType.CLOB -> ClobFieldType
            JDBCType.NCLOB -> NClobFieldType
            JDBCType.DATALINK -> UrlFieldType
            JDBCType.SQLXML -> XmlFieldType
            JDBCType.ARRAY -> ArrayFieldType(StringFieldType)
            JDBCType.NULL -> NullFieldType
            JDBCType.OTHER,
            JDBCType.JAVA_OBJECT,
            JDBCType.DISTINCT,
            JDBCType.STRUCT,
            JDBCType.REF,
            JDBCType.ROWID,
            JDBCType.REF_CURSOR,
            null -> PokemonFieldType
        }

    private fun TableName.fullyQualifiedName(): String =
        if (schema == null) name else "${schema}.${name}"

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> =
            listOf(select.sql(), from.sql(), where.sql(), orderBy.sql(), limit.sql())
        return components.filter { it.isNotBlank() }.joinToString(" ")
    }

    fun SelectNode.sql(): String =
        when (this) {
            is SelectColumns -> "SELECT " + columns.map { it.id }.joinToString(", ")
            is SelectColumnMaxValue -> "SELECT MAX(${column.id})"
        }

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> ""
            is From -> {
                val fullyQualifiedName: String =
                    if (table.schema == null) {
                        table.name
                    } else {
                        "${table.schema}.${table.name}"
                    }
                "FROM $fullyQualifiedName"
            }
        }

    fun WhereNode.sql(): String =
        when (this) {
            NoWhere -> ""
            is Where -> "WHERE ${clause.sql()}"
        }

    fun WhereClauseNode.sql(): String =
        when (this) {
            is And -> conj.map { it.sql() }.joinToString(") AND (", "(", ")")
            is Or -> disj.map { it.sql() }.joinToString(") OR (", "(", ")")
            is Equal -> "${column.id} = ?"
            is Greater -> "${column.id} > ?"
            is LesserOrEqual -> "${column.id} <= ?"
        }

    fun OrderByNode.sql(): String =
        when (this) {
            NoOrderBy -> ""
            is OrderBy -> "ORDER BY " + columns.map { it.id }.joinToString(", ")
        }

    fun LimitNode.sql(): String =
        when (this) {
            NoLimit -> ""
            is Limit -> "LIMIT $n"
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
                val type = column.type as LosslessFieldType
                listOf(io.airbyte.cdk.source.select.SelectQuery.Binding(bindingValue, type))
            }
        }
}
