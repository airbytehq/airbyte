/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.jdbc.ArrayFieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.ClobFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.JdbcMetadataQuerier
import io.airbyte.cdk.jdbc.JsonStringFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.NClobFieldType
import io.airbyte.cdk.jdbc.NStringFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.jdbc.SystemType
import io.airbyte.cdk.jdbc.UserDefinedArray
import io.airbyte.cdk.jdbc.UserDefinedType
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.FieldType
import io.airbyte.cdk.source.select.And
import io.airbyte.cdk.source.select.Equal
import io.airbyte.cdk.source.select.From
import io.airbyte.cdk.source.select.FromNode
import io.airbyte.cdk.source.select.FromSample
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
import io.airbyte.cdk.util.Jsons
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

    private fun recursiveArrayType(type: UserDefinedArray): JdbcFieldType<*> =
        when (val elementType = type.elementType) {
            is SystemType -> {
                val leafType: JdbcFieldType<*> =
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

    private fun leafType(
        typeName: String?,
        notInteger: Boolean,
    ): JdbcFieldType<*> =
        // This mapping includes literals returned by the JDBC driver as well as
        // *_TYPE_NAME column values from queries to ALL_* system tables.
        when (typeName) {
            "BINARY_FLOAT" -> FloatFieldType
            "BINARY_DOUBLE" -> DoubleFieldType
            "FLOAT",
            "DOUBLE PRECISION",
            "REAL",
            -> BigDecimalFieldType
            "NUMBER",
            "NUMERIC",
            "DECIMAL",
            "DEC",
            -> if (notInteger) BigDecimalFieldType else BigIntegerFieldType
            "INTEGER",
            "INT",
            "SMALLINT",
            -> BigIntegerFieldType
            "BOOLEAN",
            "BOOL",
            -> BooleanFieldType
            "CHAR",
            "VARCHAR2",
            "VARCHAR",
            "CHARACTER",
            "CHARACTER VARYING",
            "CHAR VARYING",
            -> StringFieldType
            "NCHAR",
            "NVARCHAR2",
            "NCHAR VARYING",
            "NATIONAL CHARACTER VARYING",
            "NATIONAL CHARACTER",
            "NATIONAL CHAR VARYING",
            "NATIONAL CHAR",
            -> NStringFieldType
            "BLOB" -> BinaryStreamFieldType
            "CLOB" -> ClobFieldType
            "NCLOB" -> NClobFieldType
            "BFILE" -> BinaryStreamFieldType
            "DATE" -> LocalDateFieldType
            "INTERVALDS",
            "INTERVAL DAY TO SECOND",
            "INTERVALYM",
            "INTERVAL YEAR TO MONTH",
            -> StringFieldType
            "JSON" -> JsonStringFieldType
            "LONG",
            "LONG RAW",
            "RAW",
            -> BinaryStreamFieldType
            "TIMESTAMP",
            "TIMESTAMP WITH LOCAL TIME ZONE",
            "TIMESTAMP WITH LOCAL TZ",
            -> LocalDateTimeFieldType
            "TIMESTAMP WITH TIME ZONE",
            "TIMESTAMP WITH TZ",
            -> OffsetDateTimeFieldType
            else -> PokemonFieldType
        }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> = listOf(select.sql(), from.sql(), where.sql(), orderBy.sql())
        val sqlWithoutLimit: String = components.filter { it.isNotBlank() }.joinToString(" ")
        val rownumClause: String =
            when (limit) {
                NoLimit -> return sqlWithoutLimit
                Limit(0) -> "ROWNUM < 1"
                is Limit -> "ROWNUM <= ?"
            }
        return if (where == NoWhere && orderBy == NoOrderBy) {
            "$sqlWithoutLimit WHERE $rownumClause"
        } else {
            "${select.sql()} FROM ($sqlWithoutLimit) WHERE $rownumClause"
        }
    }

    fun SelectNode.sql(): String =
        "SELECT " +
            when (this) {
                is SelectColumns -> columns.joinToString(", ") { it.sql() }
                is SelectColumnMaxValue -> "MAX(${column.sql()})"
            }

    fun Field.sql(): String = "\"$id\""

    fun FromNode.sql(): String =
        when (this) {
            NoFrom ->
                "FROM DUAL"
            is From ->
                if (this.namespace == null) "FROM \"$name\"" else "FROM \"$namespace\".\"$name\""
            is FromSample -> {
                val sample: String = if (sampleRateInv == 1L) "" else " SAMPLE(${sampleRatePercentage.toPlainString()})"
                val innerFrom: String = From(name, namespace).sql() + sample
                val inner = "SELECT * $innerFrom ORDER BY dbms_random.value"
                "FROM (SELECT * FROM ($inner) WHERE ROWNUM <= $sampleSize)"
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
            is LesserOrEqual -> "${column.sql()} <= ?"
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
            NoLimit, Limit(0) -> listOf()
            is Limit ->
                listOf(SelectQuery.Binding(Jsons.numberNode(n), LongFieldType))
        }
}
