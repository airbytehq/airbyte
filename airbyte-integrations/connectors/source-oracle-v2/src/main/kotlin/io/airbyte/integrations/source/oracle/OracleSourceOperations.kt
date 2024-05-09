/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.discover.ArrayFieldType
import io.airbyte.cdk.discover.BigDecimalFieldType
import io.airbyte.cdk.discover.BigIntegerFieldType
import io.airbyte.cdk.discover.BinaryStreamFieldType
import io.airbyte.cdk.discover.BooleanFieldType
import io.airbyte.cdk.discover.ClobFieldType
import io.airbyte.cdk.discover.DoubleFieldType
import io.airbyte.cdk.discover.FloatFieldType
import io.airbyte.cdk.discover.JsonStringFieldType
import io.airbyte.cdk.discover.LocalDateTimeFieldType
import io.airbyte.cdk.discover.LocalDateFieldType
import io.airbyte.cdk.discover.LongFieldType
import io.airbyte.cdk.discover.NClobFieldType
import io.airbyte.cdk.discover.NStringFieldType
import io.airbyte.cdk.discover.OffsetDateTimeFieldType
import io.airbyte.cdk.discover.PokemonFieldType
import io.airbyte.cdk.discover.LosslessFieldType
import io.airbyte.cdk.discover.StringFieldType
import io.airbyte.cdk.jdbc.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.UserDefinedArray
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.FieldTypeBase
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.JdbcMetadataQuerier
import io.airbyte.cdk.jdbc.UserDefinedType
import io.airbyte.cdk.read.stream.And
import io.airbyte.cdk.read.stream.Equal
import io.airbyte.cdk.read.stream.From
import io.airbyte.cdk.read.stream.FromNode
import io.airbyte.cdk.read.stream.Greater
import io.airbyte.cdk.read.stream.LesserOrEqual
import io.airbyte.cdk.read.stream.Limit
import io.airbyte.cdk.read.stream.LimitNode
import io.airbyte.cdk.read.stream.LimitZero
import io.airbyte.cdk.read.stream.NoFrom
import io.airbyte.cdk.read.stream.NoLimit
import io.airbyte.cdk.read.stream.NoOrderBy
import io.airbyte.cdk.read.stream.NoWhere
import io.airbyte.cdk.read.stream.Or
import io.airbyte.cdk.read.stream.OrderBy
import io.airbyte.cdk.read.stream.OrderByNode
import io.airbyte.cdk.read.stream.SelectColumnMaxValue
import io.airbyte.cdk.read.stream.SelectColumns
import io.airbyte.cdk.read.stream.SelectNode
import io.airbyte.cdk.read.stream.SelectQuery
import io.airbyte.cdk.read.stream.SelectQueryGenerator
import io.airbyte.cdk.read.stream.SelectQueryRootNode
import io.airbyte.cdk.read.stream.Where
import io.airbyte.cdk.read.stream.WhereClauseLeafNode
import io.airbyte.cdk.read.stream.WhereClauseNode
import io.airbyte.cdk.read.stream.WhereNode
import io.airbyte.commons.jackson.MoreMappers
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class OracleSourceOperations : JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator {

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> leafType(c.type.typeName, type.scale != 0)
            is UserDefinedArray -> ArrayFieldType(recursiveArrayType(type))
            is UserDefinedType -> PokemonFieldType
        }

    private fun recursiveArrayType(type: UserDefinedArray): FieldTypeBase<*> =
        when (val elementType = type.elementType) {
            is SystemType -> {
                val leafType: FieldTypeBase<*> =
                    leafType(elementType.typeName, elementType.scale != 0)
                if (leafType == OffsetDateTimeFieldType) {
                    // Oracle's JDBC driver has a bug which prevents object conversions in
                    // ArrayDataResultSet instances. Fall back to strings instead.
                    PokemonFieldType
                } else {
                    leafType
                }
            }
            is UserDefinedArray -> ArrayFieldType(recursiveArrayType(elementType))
            is UserDefinedType -> PokemonFieldType
        }

    private fun leafType(typeName: String?, notInteger: Boolean): FieldTypeBase<*> =
        // This mapping includes literals returned by the JDBC driver as well as
        // *_TYPE_NAME column values from queries to ALL_* system tables.
        when (typeName) {
            "BINARY_FLOAT" -> FloatFieldType
            "BINARY_DOUBLE" -> DoubleFieldType
            "FLOAT",
            "DOUBLE PRECISION",
            "REAL" -> BigDecimalFieldType
            "NUMBER",
            "NUMERIC",
            "DECIMAL",
            "DEC" -> if (notInteger) BigDecimalFieldType else BigIntegerFieldType
            "INTEGER",
            "INT",
            "SMALLINT" -> BigIntegerFieldType
            "BOOLEAN",
            "BOOL" -> BooleanFieldType
            "CHAR",
            "VARCHAR2",
            "VARCHAR",
            "CHARACTER",
            "CHARACTER VARYING",
            "CHAR VARYING" -> StringFieldType
            "NCHAR",
            "NVARCHAR2",
            "NCHAR VARYING",
            "NATIONAL CHARACTER VARYING",
            "NATIONAL CHARACTER",
            "NATIONAL CHAR VARYING",
            "NATIONAL CHAR" -> NStringFieldType
            "BLOB" -> BinaryStreamFieldType
            "CLOB" -> ClobFieldType
            "NCLOB" -> NClobFieldType
            "BFILE" -> BinaryStreamFieldType
            "DATE" -> LocalDateFieldType
            "INTERVALDS",
            "INTERVAL DAY TO SECOND",
            "INTERVALYM",
            "INTERVAL YEAR TO MONTH" -> StringFieldType
            "JSON" -> JsonStringFieldType
            "LONG",
            "LONG RAW",
            "RAW" -> BinaryStreamFieldType
            "TIMESTAMP",
            "TIMESTAMP WITH LOCAL TIME ZONE",
            "TIMESTAMP WITH LOCAL TZ" -> LocalDateTimeFieldType
            "TIMESTAMP WITH TIME ZONE",
            "TIMESTAMP WITH TZ" -> OffsetDateTimeFieldType
            else -> PokemonFieldType
        }

    private fun TableName.fullyQualifiedName(): String =
        // The catalog never comes into play with Oracle.
        if (schema == null) name else "${schema}.${name}"

    override fun generate(ast: SelectQueryRootNode): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQueryRootNode.sql(): String {
        val components: List<String> = listOf(select.sql(), from.sql(), where.sql(), orderBy.sql())
        val noLimitSql: String = components.filter { it.isNotBlank() }.joinToString(" ")
        val limitOperand: String = when (limit) {
            NoLimit -> return noLimitSql
            LimitZero -> "1"
            is Limit -> "?"
        }
        return if (where == NoWhere && orderBy == NoOrderBy) {
            "$noLimitSql WHERE ROWNUM < $limitOperand"
        } else {
            "${select.sql()} FROM ($noLimitSql) WHERE ROWNUM < $limitOperand"
        }
    }

    fun SelectNode.sql(): String =
        "SELECT " +
            when (this) {
                is SelectColumns -> columns.map { it.id }.joinToString(", ")
                is SelectColumnMaxValue -> "MAX(${column.id})"
            }

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> "FROM DUAL"
            is From -> "FROM ${table.fullyQualifiedName()}"
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
            is Equal -> "${column.id} = ${column.sqlOperand()}"
            is Greater -> "${column.id} > ${column.sqlOperand()}"
            is LesserOrEqual -> "${column.id} <= ${column.sqlOperand()}"
        }

    fun OrderByNode.sql(): String =
        when (this) {
            NoOrderBy -> ""
            is OrderBy -> "ORDER BY " + columns.map { it.id }.joinToString(", ")
        }

    fun SelectQueryRootNode.bindings(): List<SelectQuery.Binding> =
        where.bindings() + limit.bindings()

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
                listOf(SelectQuery.Binding(bindingValue, type))
            }
        }

    fun LimitNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            NoLimit, LimitZero -> listOf()
            is Limit ->
                listOf(SelectQuery.Binding(nodeFactory.numberNode(state.current), LongFieldType))
        }

    fun Field.sqlOperand(): String = "?"

    private val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory
}
