/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetaField
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
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.OffsetTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
import io.airbyte.cdk.jdbc.ShortFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.NativeRecordPayload
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
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

@Singleton
@Primary
class PostgresV2SourceOperations(
    private val configuration: PostgresV2SourceConfiguration? = null,
) : JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {

    private val isCdcMode: Boolean
        get() = configuration?.incrementalConfiguration is CdcIncrementalConfiguration

    // For CDC mode, use _ab_cdc_cursor as the global cursor
    override val globalCursor: FieldOrMetaField?
        get() = if (isCdcMode) PostgresV2SourceCdcMetaFields.CDC_CURSOR else null

    // For CDC mode, add CDC-specific meta fields
    override val globalMetaFields: Set<MetaField>
        get() =
            if (isCdcMode) {
                setOf(
                    CommonMetaField.CDC_UPDATED_AT,
                    CommonMetaField.CDC_DELETED_AT,
                    PostgresV2SourceCdcMetaFields.CDC_LSN,
                    PostgresV2SourceCdcMetaFields.CDC_CURSOR,
                )
            } else {
                emptySet()
            }

    // No-op for this implementation - CDC record decoration is handled by DebeziumOperations
    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {}

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload
    ) {}

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> leafType(type)
            else -> PokemonFieldType
        }

    private fun leafType(type: SystemType): JdbcFieldType<*> {
        val typeName = type.typeName?.uppercase() ?: return PokemonFieldType
        return when {
            // Boolean
            typeName in listOf("BOOL", "BOOLEAN") -> BooleanFieldType

            // Integer types
            typeName in listOf("INT2", "SMALLINT", "SMALLSERIAL") -> ShortFieldType
            typeName in listOf("INT", "INT4", "INTEGER", "SERIAL") -> IntFieldType
            typeName in listOf("INT8", "BIGINT", "BIGSERIAL", "OID") -> LongFieldType

            // Floating point types
            typeName in listOf("FLOAT4", "REAL") -> FloatFieldType
            typeName in listOf("FLOAT8", "DOUBLE PRECISION") -> DoubleFieldType

            // Decimal types
            typeName in listOf("NUMERIC", "DECIMAL") -> {
                if (type.scale == 0) BigIntegerFieldType else BigDecimalFieldType
            }
            typeName == "MONEY" -> BigDecimalFieldType

            // String types
            typeName in
                listOf(
                    "CHAR",
                    "CHARACTER",
                    "VARCHAR",
                    "CHARACTER VARYING",
                    "TEXT",
                    "NAME",
                    "CITEXT",
                    "BPCHAR"
                ) -> StringFieldType

            // UUID
            typeName == "UUID" -> StringFieldType

            // Date/Time types
            typeName == "DATE" -> LocalDateFieldType
            typeName in listOf("TIME", "TIME WITHOUT TIME ZONE") -> LocalTimeFieldType
            typeName in listOf("TIMETZ", "TIME WITH TIME ZONE") -> OffsetTimeFieldType
            typeName in listOf("TIMESTAMP", "TIMESTAMP WITHOUT TIME ZONE") -> LocalDateTimeFieldType
            typeName in listOf("TIMESTAMPTZ", "TIMESTAMP WITH TIME ZONE") -> OffsetDateTimeFieldType
            typeName == "INTERVAL" -> StringFieldType

            // Binary types
            typeName == "BYTEA" -> BinaryStreamFieldType

            // JSON types
            typeName in listOf("JSON", "JSONB") -> StringFieldType

            // XML
            typeName == "XML" -> StringFieldType

            // Network address types
            typeName in listOf("INET", "CIDR", "MACADDR", "MACADDR8") -> StringFieldType

            // Geometric types
            typeName in listOf("POINT", "LINE", "LSEG", "BOX", "PATH", "POLYGON", "CIRCLE") ->
                StringFieldType

            // Range types
            typeName in
                listOf("INT4RANGE", "INT8RANGE", "NUMRANGE", "TSRANGE", "TSTZRANGE", "DATERANGE") ->
                StringFieldType

            // Bit string types
            typeName in listOf("BIT", "VARBIT", "BIT VARYING") -> StringFieldType

            // Text search types
            typeName in listOf("TSVECTOR", "TSQUERY") -> StringFieldType

            // Array types - handle as string
            typeName.startsWith("_") || typeName.endsWith("[]") -> StringFieldType

            // Enumerated types and other custom types
            else -> PokemonFieldType
        }
    }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> = listOf(select.sql(), from.sql(), where.sql(), orderBy.sql())
        val sqlWithoutLimit: String = components.filter { it.isNotBlank() }.joinToString(" ")
        val limitClause: String =
            when (limit) {
                NoLimit -> return sqlWithoutLimit
                Limit(0) -> "LIMIT 0"
                is Limit -> "LIMIT ?"
            }
        return "$sqlWithoutLimit $limitClause"
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
            NoFrom -> ""
            is From ->
                if (this.namespace == null) "FROM \"$name\"" else "FROM \"$namespace\".\"$name\""
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
