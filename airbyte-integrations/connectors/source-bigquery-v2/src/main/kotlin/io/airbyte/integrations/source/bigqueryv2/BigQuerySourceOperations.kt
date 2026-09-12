/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.DataField
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
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
import io.airbyte.protocol.models.v0.AirbyteStream
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.time.OffsetDateTime

/**
 * BigQuery flavour of the `extract-jdbc` toolkit hooks:
 * - [JdbcMetadataQuerier.FieldTypeMapper] for column metadata coming from the JDBC driver (the
 * discovery path uses [BigQueryFieldTypes.fromField] on the native table schema instead);
 * - [SelectQueryGenerator] rendering GoogleSQL: backtick-quoted identifiers, `dataset.table`
 * references relative to the connection's project, literal `LIMIT`, `TABLESAMPLE SYSTEM`;
 * - [JdbcAirbyteStreamFactory], which additionally renders the nested JSON schema of `STRUCT` and
 * `ARRAY` columns.
 */
@Singleton
@Primary
class BigQuerySourceOperations :
    JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {

    override val globalCursor: MetaField? = null

    override val globalMetaFields: Set<MetaField> = emptySet()

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> BigQueryFieldTypes.fromTypeName(type.typeName)
            else -> PokemonFieldType
        }

    override fun create(
        config: SourceConfiguration,
        discoveredStream: DiscoveredStream
    ): AirbyteStream {
        val stream: AirbyteStream = super.create(config, discoveredStream)
        val properties: ObjectNode = stream.jsonSchema.get("properties") as ObjectNode
        for (field in discoveredStream.columns) {
            when (field.type) {
                is BigQueryStructFieldType,
                is BigQueryArrayFieldType ->
                    properties.set<JsonNode>(field.id, BigQueryFieldTypes.jsonSchema(field.type))
                else -> Unit
            }
        }
        return stream
    }

    override fun generate(ast: SelectQuerySpec): SelectQuery =
        SelectQuery(ast.sql(), ast.select.columns, ast.bindings())

    fun SelectQuerySpec.sql(): String {
        val components: List<String> =
            listOf(select.sql(), from.sql(), where.sql(), orderBy.sql(), limit.sql())
        return components.filter { it.isNotBlank() }.joinToString(" ")
    }

    fun SelectNode.sql(): String =
        "SELECT " +
            when (this) {
                is SelectColumns -> columns.joinToString(", ") { it.sql() }
                is SelectColumnMaxValue -> "MAX(${column.sql()})"
            }

    fun DataField.sql(): String = id.quoted()

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> ""
            is From -> "FROM ${tableReference(name, namespace)}"
            is FromSample -> {
                // TABLESAMPLE SYSTEM is a BigQuery block-level sample; the percentage is a literal.
                val sample: String =
                    if (sampleRateInv == 1L) ""
                    else " TABLESAMPLE SYSTEM (${sampleRatePercentage.toPlainString()} PERCENT)"
                val inner: String =
                    listOf(
                            "SELECT * FROM ${tableReference(name, namespace)}$sample",
                            where?.sql() ?: "",
                            "LIMIT $sampleSize",
                        )
                        .filter { it.isNotBlank() }
                        .joinToString(" ")
                "FROM ($inner)"
            }
        }

    fun WhereNode.sql(): String =
        when (this) {
            is NoWhere -> ""
            is Where -> "WHERE ${clause.sql()}"
        }

    fun WhereClauseNode.sql(): String =
        when (this) {
            is And -> conj.joinToString(") AND (", "(", ")") { it.sql() }
            is Or -> disj.joinToString(") OR (", "(", ")") { it.sql() }
            is Equal -> "${column.sql()} = ?"
            is GreaterOrEqual -> "${column.sql()} >= ?"
            is Greater -> "${column.sql()} > ?"
            is LesserOrEqual -> "${column.sql()} <= ?"
            is Lesser -> "${column.sql()} < ?"
        }

    fun OrderByNode.sql(): String =
        when (this) {
            NoOrderBy -> ""
            is OrderBy -> "ORDER BY " + columns.joinToString(", ") { it.sql() }
        }

    /** BigQuery only accepts a literal (or named parameter) row count in `LIMIT`. */
    fun LimitNode.sql(): String =
        when (this) {
            NoLimit -> ""
            is Limit -> "LIMIT $n"
        }

    fun SelectQuerySpec.bindings(): List<SelectQuery.Binding> = from.bindings() + where.bindings()

    fun FromNode.bindings(): List<SelectQuery.Binding> =
        when (this) {
            is FromSample -> where?.bindings() ?: listOf()
            else -> listOf()
        }

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

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: ObjectNode
    ) {
        return
    }

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload
    ) {
        return
    }

    companion object {
        /** `dataset.table`, relative to the connection's project. */
        fun tableReference(name: String, namespace: String?): String =
            if (namespace == null) name.quoted() else "${namespace.quoted()}.${name.quoted()}"

        /** Backtick quoting; a backtick inside an identifier is escaped with a backslash. */
        fun String.quoted(): String = "`" + replace("\\", "\\\\").replace("`", "\\`") + "`"
    }
}
