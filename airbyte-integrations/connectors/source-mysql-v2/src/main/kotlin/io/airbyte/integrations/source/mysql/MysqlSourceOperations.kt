/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import com.mysql.cj.MysqlType
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.NullFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.ShortFieldType
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
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.WhereClauseLeafNode
import io.airbyte.cdk.read.WhereClauseNode
import io.airbyte.cdk.read.WhereNode
import io.airbyte.cdk.util.Jsons
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

@Singleton
@Primary
class MysqlSourceOperations : JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator {
    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> leafType(type)
            else -> PokemonFieldType
        }

    private fun leafType(type: SystemType): JdbcFieldType<*> {
        val typeName = type.typeName
        return when (typeName) {
            MysqlType.BIT.name -> {
                if (type.precision!! > 1) {
                    BinaryStreamFieldType
                } else {
                    BooleanFieldType
                }
            }
            MysqlType.BOOLEAN.name -> BooleanFieldType
            MysqlType.TINYINT.name -> {
                if (type.precision!! > 1) {
                    BinaryStreamFieldType
                } else {
                    ShortFieldType
                }
            }
            MysqlType.TINYINT_UNSIGNED.name,
            MysqlType.YEAR.name -> ShortFieldType
            MysqlType.SMALLINT.name,
            MysqlType.SMALLINT_UNSIGNED.name,
            MysqlType.MEDIUMINT.name,
            MysqlType.MEDIUMINT_UNSIGNED.name,
            MysqlType.INT.name -> IntFieldType
            MysqlType.INT_UNSIGNED.name,
            MysqlType.BIGINT.name,
            MysqlType.BIGINT_UNSIGNED.name -> BigIntegerFieldType
            MysqlType.FLOAT.name,
            MysqlType.FLOAT_UNSIGNED.name -> FloatFieldType
            MysqlType.DOUBLE.name,
            MysqlType.DOUBLE_UNSIGNED.name -> DoubleFieldType
            MysqlType.DECIMAL.name,
            MysqlType.DECIMAL_UNSIGNED.name -> {
                if (type.scale == 0) BigIntegerFieldType else BigDecimalFieldType
            }
            MysqlType.DATE.name -> LocalDateFieldType
            MysqlType.DATETIME.name -> LocalDateTimeFieldType
            MysqlType.TIMESTAMP.name -> OffsetDateTimeFieldType
            MysqlType.TIME.name -> LocalTimeFieldType
            MysqlType.CHAR.name,
            MysqlType.VARCHAR.name,
            MysqlType.TINYTEXT.name,
            MysqlType.TEXT.name,
            MysqlType.MEDIUMTEXT.name,
            MysqlType.LONGTEXT.name,
            MysqlType.JSON.name,
            MysqlType.ENUM.name,
            MysqlType.SET.name -> StringFieldType
            MysqlType.TINYBLOB.name,
            MysqlType.BLOB.name,
            MysqlType.MEDIUMBLOB.name,
            MysqlType.LONGBLOB.name,
            MysqlType.BINARY.name,
            MysqlType.VARBINARY.name,
            MysqlType.GEOMETRY.name -> BinaryStreamFieldType
            MysqlType.NULL.name -> NullFieldType
            else -> PokemonFieldType
        }
    }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> = listOf(select.sql(), from.sql(), where.sql(), orderBy.sql())
        val sqlWithoutLimit: String = components.filter { it.isNotBlank() }.joinToString(" ")
        val rownumClause: String =
            when (limit) {
                NoLimit -> return sqlWithoutLimit
                Limit(0) -> "LIMIT 0"
                is Limit -> "LIMIT ?"
            }
        return "$sqlWithoutLimit $rownumClause"
    }

    fun SelectNode.sql(): String =
        "SELECT " +
            when (this) {
                is SelectColumns -> columns.joinToString(", ") { it.sql() }
                is SelectColumnMaxValue -> "MAX(${column.sql()})"
            }

    fun Field.sql(): String = "`$id`"

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> ""
            is From -> if (this.namespace == null) "FROM `$name`" else "FROM `$namespace`.`$name`"
            is FromSample -> TODO("not implemented in mysql")
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
            Limit(0) -> listOf()
            is Limit -> listOf(SelectQuery.Binding(Jsons.numberNode(n), LongFieldType))
        }
}
