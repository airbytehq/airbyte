/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
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
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.PokemonFieldType
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
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.micronaut.context.annotation.Primary
import jakarta.inject.Inject
import jakarta.inject.Provider
import jakarta.inject.Singleton
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

/**
 * BigQuery flavour of the `extract-jdbc` toolkit hooks:
 * - [JdbcMetadataQuerier.FieldTypeMapper] for column metadata coming from the JDBC driver (the
 * discovery path uses [BigQueryFieldTypes.fromField] on the native table schema instead);
 * - [SelectQueryGenerator] rendering GoogleSQL: backtick-quoted identifiers, fully qualified
 * `project.dataset.table` references (the connection's project is the job project, which may differ
 * from the data project), literal `LIMIT`, `TABLESAMPLE SYSTEM`;
 * - [JdbcAirbyteStreamFactory], which additionally renders the nested JSON schema of `STRUCT` and
 * `ARRAY` columns.
 */
@Singleton
@Primary
class BigQuerySourceOperations
private constructor(
    private val tableTypes: BigQueryTableTypes,
    /**
     * The project owning the datasets, from [BigQuerySourceConfiguration.projectId]. Resolved
     * lazily: this bean is wired into the CHECK and DISCOVER operations before the configuration is
     * validated, and an invalid configuration must fail inside the operation, not at wiring time.
     */
    private val dataProjectId: () -> String,
) : JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {

    @Inject
    constructor(
        tableTypes: BigQueryTableTypes,
        configProvider: Provider<SourceConfiguration>,
    ) : this(
        tableTypes,
        {
            (configProvider.get() as? BigQuerySourceConfiguration)?.projectId
                ?: throw ConfigErrorException("Missing required 'project_id' property.")
        },
    )

    /** For tests: every stream is assumed to be a table of [dataProjectId]. */
    constructor(
        dataProjectId: String,
        tableTypes: BigQueryTableTypes = BigQueryTableTypes(),
    ) : this(tableTypes, { dataProjectId })

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
                is SelectColumns -> columns.joinToString(", ") { it.selectSql() }
                is SelectColumnMaxValue ->
                    if (column.isReadAsText()) "CAST(MAX(${column.sql()}) AS STRING)"
                    else "MAX(${column.sql()})"
            }

    /**
     * A column in the SELECT list. `DATE`, `DATETIME` and `TIME` are read as text so that the JDBC
     * driver's calendar and precision limitations do not apply (see [BigQueryTextTemporalFieldType]
     * ); WHERE and ORDER BY keep the native column.
     */
    fun DataField.selectSql(): String =
        when {
            isReadAsText() -> "CAST(${sql()} AS STRING) AS ${sql()}"
            // Exact rendering of nested values, see BigQueryNestedValueGetter.
            type is BigQueryStructFieldType || type is BigQueryArrayFieldType ->
                "TO_JSON_STRING(${sql()}) AS ${sql()}"
            else -> sql()
        }

    fun DataField.isReadAsText(): Boolean = type is BigQueryTextTemporalFieldType<*>

    fun DataField.sql(): String = id.quoted()

    fun FromNode.sql(): String =
        when (this) {
            NoFrom -> ""
            is From -> "FROM ${tableReference(name, namespace)}"
            is FromSample -> {
                // TABLESAMPLE SYSTEM is a BigQuery block-level sample; the percentage is a literal.
                // It "can only be applied directly to base tables": views, materialized views,
                // external tables and snapshots are sampled with a plain LIMIT instead.
                val streamID =
                    StreamIdentifier.from(
                        StreamDescriptor().withName(name).withNamespace(namespace)
                    )
                val sample: String =
                    if (sampleRateInv == 1L || !tableTypes.supportsTableSample(streamID)) ""
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
            is Equal -> "${column.sql()} = ${column.bindPlaceholder()}"
            is GreaterOrEqual -> "${column.sql()} >= ${column.bindPlaceholder()}"
            is Greater -> "${column.sql()} > ${column.bindPlaceholder()}"
            is LesserOrEqual -> "${column.sql()} <= ${column.bindPlaceholder()}"
            is Lesser -> "${column.sql()} < ${column.bindPlaceholder()}"
        }

    /**
     * The BigQuery type a `WHERE`-clause bound must be cast to, or null to bind it natively. No
     * JDBC setter produces a `DATE`/`DATETIME`/`TIME` or `BIGNUMERIC` parameter, and `setTimestamp`
     * truncates a `TIMESTAMP` to milliseconds; for those the value is bound as a `STRING` (see
     * [bindings]) and cast back here so the comparison is same-typed and full-precision. The bound
     * text for the decimal case is a plain number (the CDK never emits scientific notation), which
     * `CAST` accepts.
     */
    private fun DataField.whereCastType(): String? =
        when (val t = type) {
            is BigQueryTextTemporalFieldType<*> -> t.bigQueryTypeName
            BigQueryBigNumericFieldType -> "BIGNUMERIC"
            OffsetDateTimeFieldType -> "TIMESTAMP"
            else -> null
        }

    /**
     * The `?` placeholder for a bound value in a `WHERE` clause, cast when [whereCastType] applies.
     */
    private fun DataField.bindPlaceholder(): String =
        whereCastType()?.let { "CAST(? AS $it)" } ?: "?"

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
                // Columns with a whereCastType are bound as STRING and cast back to their type in
                // the
                // SQL (see bindPlaceholder); everything else binds with its own JDBC setter. The
                // value
                // is normalized to a text node so a plain-number decimal binds as text too.
                if (column.whereCastType() != null) {
                    listOf(
                        SelectQuery.Binding(Jsons.textNode(bindingValue.asText()), StringFieldType)
                    )
                } else {
                    listOf(
                        SelectQuery.Binding(
                            bindingValue,
                            column.type as LosslessJdbcFieldType<*, *>
                        )
                    )
                }
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

    /**
     * A query returning `APPROX_QUANTILES([pk], [numQuantiles])` of the (optionally [where]
     * -bounded) table, one boundary value per row. The JDBC fallback's concurrent creator uses it
     * to split a table into balanced key ranges without a full-table sample: `APPROX_QUANTILES`
     * reads only the key column. The boundary column is rendered exactly as a normal read renders
     * it ([selectSql]), so a DATE/DATETIME/TIME boundary comes back as the same string the read
     * path emits and is usable verbatim as a `WHERE` bound (which the generator then binds as text
     * and casts back, see [bindPlaceholder]). `APPROX_QUANTILES(x, n)` yields `n + 1` values (the
     * min, `n - 1` interior boundaries and the max); the caller drops the extremes.
     */
    fun approxQuantilesQuery(
        name: String,
        namespace: String?,
        pk: DataField,
        numQuantiles: Int,
        where: WhereNode,
    ): SelectQuery {
        val inner: String =
            listOf(
                    "SELECT APPROX_QUANTILES(${pk.sql()}, $numQuantiles)",
                    "FROM ${tableReference(name, namespace)}",
                    where.sql(),
                )
                .filter { it.isNotBlank() }
                .joinToString(" ")
        val sql = "SELECT ${pk.selectSql()} FROM UNNEST(($inner)) AS ${pk.sql()}"
        return SelectQuery(sql, listOf(pk), where.bindings())
    }

    /**
     * `MAX(cursor)` of the table as it was at [snapshotTime] (BigQuery time travel, `FOR
     * SYSTEM_TIME AS OF`), rendered like the toolkit's cursor upper bound query so that the value
     * comes back through the same getter and encoder as the JDBC cursor path's: the Storage Read
     * API initial snapshot of an incremental stream reads the table at that same instant, and the
     * value becomes the stream's cursor checkpoint. The literal is UTC with microseconds.
     */
    fun cursorUpperBoundAsOfQuery(
        name: String,
        namespace: String?,
        cursor: DataField,
        snapshotTime: Instant,
    ): SelectQuery {
        val max: String =
            if (cursor.isReadAsText()) "CAST(MAX(${cursor.sql()}) AS STRING)"
            else "MAX(${cursor.sql()})"
        val sql =
            "SELECT $max AS ${cursor.sql()} FROM ${tableReference(name, namespace)} " +
                "FOR SYSTEM_TIME AS OF TIMESTAMP '${timestampLiteral(snapshotTime)}'"
        return SelectQuery(sql, listOf(cursor), emptyList())
    }

    fun timestampLiteral(instant: Instant): String =
        TIMESTAMP_LITERAL.format(instant.atOffset(ZoneOffset.UTC))

    /**
     * `project.dataset.table`: the data project is always spelled out because the connection's
     * `ProjectId` is the job project, in which unqualified names would be resolved.
     */
    fun tableReference(name: String, namespace: String?): String =
        if (namespace == null) name.quoted()
        else "${dataProjectId().quoted()}.${namespace.quoted()}.${name.quoted()}"

    companion object {
        private val TIMESTAMP_LITERAL: DateTimeFormatter =
            DateTimeFormatter.ofPattern("uuuu-MM-dd HH:mm:ss.SSSSSS'+00'")

        /** Backtick quoting; a backtick inside an identifier is escaped with a backslash. */
        fun String.quoted(): String = "`" + replace("\\", "\\\\").replace("`", "\\`") + "`"
    }
}
