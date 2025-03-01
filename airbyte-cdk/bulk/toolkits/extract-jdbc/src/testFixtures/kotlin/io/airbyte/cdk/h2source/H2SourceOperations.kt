/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.h2source

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.CdcStringMetaFieldType
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.jdbc.ArrayFieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BinaryStreamFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.ByteFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.ClobFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.NClobFieldType
import io.airbyte.cdk.jdbc.NStringFieldType
import io.airbyte.cdk.jdbc.NullFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.OffsetTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.ShortFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.jdbc.UrlFieldType
import io.airbyte.cdk.jdbc.XmlFieldType
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
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.sql.JDBCType
import java.time.OffsetDateTime

/** Stateless connector-specific logic for [H2Source]. */
@Singleton
@Requires(env = [Environment.TEST])
@Secondary
class H2SourceOperations :
    JdbcMetadataQuerier.FieldTypeMapper,
    SelectQueryGenerator,
    JdbcAirbyteStreamFactory,
    MetaFieldDecorator {

    data object H2GlobalCursor : MetaField {
        override val id: String = "_ab_cdc_fake_cursor"
        override val type: FieldType = CdcStringMetaFieldType
    }

    override val globalCursor: MetaField = H2GlobalCursor

    override val globalMetaFields: Set<MetaField> =
        setOf(H2GlobalCursor, CommonMetaField.CDC_UPDATED_AT, CommonMetaField.CDC_DELETED_AT)

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        recordData.putNull(H2GlobalCursor.id)
        recordData.putNull(CommonMetaField.CDC_UPDATED_AT.id)
        recordData.putNull(CommonMetaField.CDC_DELETED_AT.id)
    }

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (c.type.jdbcType) {
            JDBCType.BIT,
            JDBCType.BOOLEAN, -> BooleanFieldType
            JDBCType.TINYINT -> ByteFieldType
            JDBCType.SMALLINT -> ShortFieldType
            JDBCType.INTEGER -> IntFieldType
            JDBCType.BIGINT -> BigIntegerFieldType
            JDBCType.FLOAT -> FloatFieldType
            JDBCType.DOUBLE -> DoubleFieldType
            JDBCType.REAL,
            JDBCType.NUMERIC,
            JDBCType.DECIMAL, -> BigDecimalFieldType
            JDBCType.CHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR, -> StringFieldType
            JDBCType.NCHAR,
            JDBCType.NVARCHAR,
            JDBCType.LONGNVARCHAR, -> NStringFieldType
            JDBCType.DATE -> LocalDateFieldType
            JDBCType.TIME -> LocalTimeFieldType
            JDBCType.TIMESTAMP -> LocalDateTimeFieldType
            JDBCType.TIME_WITH_TIMEZONE -> OffsetTimeFieldType
            JDBCType.TIMESTAMP_WITH_TIMEZONE -> OffsetDateTimeFieldType
            JDBCType.BLOB -> BinaryStreamFieldType
            JDBCType.BINARY,
            JDBCType.VARBINARY,
            JDBCType.LONGVARBINARY, -> BytesFieldType
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
            null, -> PokemonFieldType
        }

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
            is From -> if (namespace == null) "FROM $name" else "FROM $namespace.$name"
            is FromSample -> {
                val innerFrom: String = From(name, namespace).sql()
                val innerWhere = "WHERE MOD(ROWNUM(), $sampleRateInv) = 0 "
                val innerLimit = "LIMIT $sampleSize"
                "FROM (SELECT * $innerFrom $innerWhere $innerLimit)"
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
            is GreaterOrEqual -> "${column.id} >= ?"
            is Greater -> "${column.id} > ?"
            is LesserOrEqual -> "${column.id} <= ?"
            is Lesser -> "${column.id} < ?"
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
                val type = column.type as LosslessJdbcFieldType<*, *>
                listOf(SelectQuery.Binding(bindingValue, type))
            }
        }
}
