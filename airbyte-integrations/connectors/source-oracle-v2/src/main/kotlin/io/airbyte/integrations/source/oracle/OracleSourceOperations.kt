/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.ArrayValueType
import io.airbyte.cdk.discover.BigDecimalValueType
import io.airbyte.cdk.discover.BigIntegerValueType
import io.airbyte.cdk.discover.BinaryStreamValueType
import io.airbyte.cdk.discover.BooleanValueType
import io.airbyte.cdk.discover.ClobValueType
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.DiscoverMapper
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.DoubleValueType
import io.airbyte.cdk.discover.FloatValueType
import io.airbyte.cdk.discover.GenericUserDefinedType
import io.airbyte.cdk.discover.JsonStringValueType
import io.airbyte.cdk.discover.LeafAirbyteType
import io.airbyte.cdk.discover.LocalDateTimeValueType
import io.airbyte.cdk.discover.LocalDateValueType
import io.airbyte.cdk.discover.LongValueType
import io.airbyte.cdk.discover.NClobValueType
import io.airbyte.cdk.discover.NStringValueType
import io.airbyte.cdk.discover.OffsetDateTimeValueType
import io.airbyte.cdk.discover.OneWayStringValueType
import io.airbyte.cdk.discover.ReversibleValueType
import io.airbyte.cdk.discover.StringValueType
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.discover.UserDefinedArray
import io.airbyte.cdk.discover.ValueType
import io.airbyte.cdk.read.DataColumn
import io.airbyte.cdk.read.stream.And
import io.airbyte.cdk.read.stream.Equal
import io.airbyte.cdk.read.stream.From
import io.airbyte.cdk.read.stream.FromNode
import io.airbyte.cdk.read.stream.Greater
import io.airbyte.cdk.read.stream.LesserOrEqual
import io.airbyte.cdk.read.stream.Limit
import io.airbyte.cdk.read.stream.LimitNode
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
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
@Primary
class OracleSourceOperations : DiscoverMapper, SelectQueryGenerator {

    override fun selectFromTableLimit0(table: TableName, columns: List<String>): String =
        // Oracle doesn't do LIMIT, instead we need to involve ROWNUM.
        "SELECT ${columns.joinToString()} FROM ${table.fullyQualifiedName()} WHERE ROWNUM < 1"

    override fun columnValueType(c: ColumnMetadata): ValueType<*> =
        when (val type = c.type) {
            is UserDefinedArray -> ArrayValueType(recursiveArrayType(type))
            is GenericUserDefinedType -> OneWayStringValueType
            is SystemType -> leafType(c.type.typeName, type.scale != 0)
        }

    private fun recursiveArrayType(type: UserDefinedArray): ValueType<*> =
        when (val elementType = type.elementType) {
            is UserDefinedArray -> ArrayValueType(recursiveArrayType(elementType))
            is GenericUserDefinedType -> OneWayStringValueType
            is SystemType -> {
                val leafType: ValueType<*> = leafType(elementType.typeName, elementType.scale != 0)
                if (leafType == OffsetDateTimeValueType) {
                    // Oracle's JDBC driver has a bug which prevents object conversions in
                    // ArrayDataResultSet instances. Fall back to strings instead.
                    OneWayStringValueType
                } else {
                    leafType
                }
            }
        }

    private fun leafType(typeName: String?, notInteger: Boolean): ValueType<*> =
        // This mapping includes literals returned by the JDBC driver as well as
        // *_TYPE_NAME column values from queries to ALL_* system tables.
        when (typeName) {
            "BINARY_FLOAT" -> FloatValueType
            "BINARY_DOUBLE" -> DoubleValueType
            "FLOAT",
            "DOUBLE PRECISION",
            "REAL" -> BigDecimalValueType
            "NUMBER",
            "NUMERIC",
            "DECIMAL",
            "DEC" -> if (notInteger) BigDecimalValueType else BigIntegerValueType
            "INTEGER",
            "INT",
            "SMALLINT" -> BigIntegerValueType
            "BOOLEAN",
            "BOOL" -> BooleanValueType
            "CHAR",
            "VARCHAR2",
            "VARCHAR",
            "CHARACTER",
            "CHARACTER VARYING",
            "CHAR VARYING" -> StringValueType
            "NCHAR",
            "NVARCHAR2",
            "NCHAR VARYING",
            "NATIONAL CHARACTER VARYING",
            "NATIONAL CHARACTER",
            "NATIONAL CHAR VARYING",
            "NATIONAL CHAR" -> NStringValueType
            "BLOB" -> BinaryStreamValueType
            "CLOB" -> ClobValueType
            "NCLOB" -> NClobValueType
            "BFILE" -> BinaryStreamValueType
            "DATE" -> LocalDateValueType
            "INTERVALDS",
            "INTERVAL DAY TO SECOND",
            "INTERVALYM",
            "INTERVAL YEAR TO MONTH" -> StringValueType
            "JSON" -> JsonStringValueType
            "LONG",
            "LONG RAW",
            "RAW" -> BinaryStreamValueType
            "TIMESTAMP",
            "TIMESTAMP WITH LOCAL TIME ZONE",
            "TIMESTAMP WITH LOCAL TZ" -> LocalDateTimeValueType
            "TIMESTAMP WITH TIME ZONE",
            "TIMESTAMP WITH TZ" -> OffsetDateTimeValueType
            else -> OneWayStringValueType
        }

    override fun isPossiblePrimaryKeyElement(c: ColumnMetadata): Boolean =
        when (columnValueType(c)) {
            !is ReversibleValueType<*, *> -> false
            BinaryStreamValueType,
            ClobValueType,
            JsonStringValueType,
            NClobValueType -> false
            else -> true
        }

    override fun isPossibleCursor(c: ColumnMetadata): Boolean =
        isPossiblePrimaryKeyElement(c) &&
            when (columnValueType(c)) {
                BooleanValueType -> false
                else -> true
            }

    private fun TableName.fullyQualifiedName(): String =
        // The catalog never comes into play with Oracle.
        if (schema == null) name else "${schema}.${name}"

    override fun globalAirbyteStream(stream: DiscoveredStream): AirbyteStream =
        DiscoverMapper.basicAirbyteStream(this, stream).apply {
            namespace = stream.table.schema
            supportedSyncModes = listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
            (jsonSchema["properties"] as ObjectNode).apply {
                set<ObjectNode>("_ab_cdc_lsn", LeafAirbyteType.NUMBER.asJsonSchema())
                set<ObjectNode>(
                    "_ab_cdc_updated_at",
                    LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE.asJsonSchema()
                )
                set<ObjectNode>(
                    "_ab_cdc_deleted_at",
                    LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE.asJsonSchema()
                )
            }
            defaultCursorField = listOf("_ab_cdc_lsn")
            sourceDefinedCursor = true
        }

    override fun nonGlobalAirbyteStream(stream: DiscoveredStream): AirbyteStream =
        DiscoverMapper.basicAirbyteStream(this, stream).apply {
            namespace = stream.table.schema
            supportedSyncModes =
                if (defaultCursorField.isEmpty()) {
                    listOf(SyncMode.FULL_REFRESH)
                } else {
                    listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                }
        }

    override fun generateSql(ast: SelectQueryRootNode): SelectQuery =
        SelectQuery(ast.sql(), ast.columns(), ast.bindings())

    fun SelectQueryRootNode.sql(): String {
        val components: List<String> = listOf(select.sql(), from.sql(), where.sql(), orderBy.sql())
        val noLimitSql: String = components.filter { it.isNotBlank() }.joinToString(" ")
        return when (limit) {
            NoLimit -> noLimitSql
            is Limit -> "${select.sql()} FROM ($noLimitSql) WHERE ROWNUM < ?"
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

    fun SelectQueryRootNode.columns(): List<SelectQuery.Column> =
        select.columns.map { SelectQuery.Column(it.id, columnValueType(it.metadata)) }

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
                val type = columnValueType(column.metadata) as ReversibleValueType<*, *>
                listOf(SelectQuery.Binding(bindingValue, type))
            }
        }

    fun LimitNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            is NoLimit -> listOf()
            is Limit ->
                listOf(SelectQuery.Binding(nodeFactory.numberNode(state.current), LongValueType))
        }

    fun DataColumn.sqlOperand(): String = "?"

    private val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory
}
