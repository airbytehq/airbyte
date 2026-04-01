/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetaField
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.BooleanFieldType
import io.airbyte.cdk.jdbc.ByteFieldType
import io.airbyte.cdk.jdbc.BytesFieldType
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcFieldType
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalTimeFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
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
import io.airbyte.cdk.data.LocalDateCodec
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.core.annotation.Nullable
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.LocalDate
import java.time.OffsetDateTime

@Singleton
@Primary
class SnowflakeSourceOperations
@Inject
constructor(
    @Nullable sourceConfig: SourceConfiguration? = null,
) : JdbcMetadataQuerier.FieldTypeMapper, SelectQueryGenerator, JdbcAirbyteStreamFactory {
    private val configuration: SnowflakeSourceConfiguration? =
        when {
            sourceConfig == null -> null
            sourceConfig is SnowflakeSourceConfiguration -> sourceConfig
            else ->
                throw IllegalStateException(
                    "Expected SnowflakeSourceConfiguration but got" +
                        " ${sourceConfig::class.qualifiedName}"
                )
        }

    /**
     * Cache of cursor field per table (namespace to name), populated when a SELECT MAX(cursor)
     * query is seen. Used to apply date bounds to unsplittable snapshot reads which have no
     * ORDER BY and no SELECT MAX in their SelectQuerySpec.
     *
     * This cache is never cleared; it is scoped to a single sync run (one
     * [SnowflakeSourceOperations] instance lifetime).
     */
    private val cursorFieldByTable =
        java.util.concurrent.ConcurrentHashMap<Pair<String?, String>, Field>()

    private val startDate: LocalDate? = configuration?.startDate?.let { LocalDate.parse(it) }
    private val endDate: LocalDate? = configuration?.endDate?.let { LocalDate.parse(it) }
    private val log = KotlinLogging.logger {}

    override val globalCursor: MetaField? = null

    override val globalMetaFields: Set<MetaField> = emptySet()

    override fun toFieldType(c: JdbcMetadataQuerier.ColumnMetadata): FieldType =
        when (val type = c.type) {
            is SystemType -> {
                leafType(type.typeName)
            }
            else -> PokemonFieldType
        }

    private fun leafType(typeName: String?): JdbcFieldType<*> {
        return when (typeName?.uppercase()) {
            "VARCHAR",
            "CHAR",
            "CHARACTER",
            "STRING",
            "TEXT", -> StringFieldType
            "BOOLEAN", -> BooleanFieldType
            "NUMBER",
            "DECIMAL",
            "NUMERIC", -> BigDecimalFieldType
            "INT",
            "INTEGER", -> IntFieldType
            "BIGINT", -> BigIntegerFieldType
            "SMALLINT",
            "TINYINT" -> ShortFieldType
            "BYTEINT" -> ByteFieldType
            "FLOAT",
            "FLOAT4",
            "FLOAT8",
            "DOUBLE",
            "DOUBLE PRECISION",
            "REAL", -> DoubleFieldType
            "DATE", -> LocalDateFieldType
            "TIME", -> LocalTimeFieldType
            "TIMESTAMP_LTZ",
            "TIMESTAMP_TZ",
            "TIMESTAMPLTZ",
            "TIMESTAMPTZ", -> SnowflakeOffsetDateTimeFieldType
            "DATETIME",
            "TIMESTAMP",
            "TIMESTAMP_NTZ",
            "TIMESTAMPNTZ", -> SnowflakeLocalDateTimeFieldType
            "BINARY",
            "VARBINARY", -> BytesFieldType
            "VARIANT",
            "OBJECT",
            "GEOGRAPHY",
            "GEOMETRY",
            "VECTOR",
            "FILE",
            "ARRAY", -> StringFieldType
            else -> PokemonFieldType
        }
    }

    override fun generate(ast: SelectQuerySpec): SelectQuery {
        val modifiedAst = applyDateBounds(ast)
        return SelectQuery(modifiedAst.sql(), modifiedAst.select.columns, modifiedAst.bindings())
    }

    private fun tableKey(from: FromNode): Pair<String?, String>? =
        when (from) {
            is From -> from.namespace to from.name
            is FromSample -> from.namespace to from.name
            else -> null
        }

    private fun applyDateBounds(ast: SelectQuerySpec): SelectQuerySpec {
        if (startDate == null && endDate == null) return ast

        val key = tableKey(ast.from)
        val fullRefreshColName = configuration?.fullRefreshTemporalColumn

        // Detect the cursor field:
        // 1. SELECT MAX — authoritative cursor; cache only when it is the temporal column or no
        //    temporal column is configured. PK MAX queries (used for full-refresh splitting) must
        //    NOT be cached, otherwise they pollute the cache for subsequent read queries.
        // 2. Cached cursor — covers splittable reads where ORDER BY is the PK, not the cursor.
        // 3. Full-refresh temporal column — look it up directly in the SELECT list (before the
        //    ORDER BY fallback so PK columns in ORDER BY are not mistaken for the cursor).
        // 4. ORDER BY fallback — for incremental without a cache entry yet (first partition).
        val cursorField: Field? =
            when {
                ast.select is SelectColumnMaxValue -> {
                    val field = (ast.select as SelectColumnMaxValue).column
                    val isCursorMax = fullRefreshColName == null || field.id == fullRefreshColName
                    if (isCursorMax) {
                        key?.let { cursorFieldByTable[it] = field }
                        field
                    } else {
                        null // PK MAX for full-refresh splitting — skip date filtering
                    }
                }
                key != null && cursorFieldByTable.containsKey(key) -> cursorFieldByTable[key]
                fullRefreshColName != null && ast.select is SelectColumns -> {
                    val columns = (ast.select as SelectColumns).columns
                    val byName = columns.find { it.id == fullRefreshColName }
                    when {
                        byName == null -> {
                            // NullFieldType appears during LIMIT 0 discovery queries — skip those
                            // silently. Only warn for real queries where types are resolved.
                            if (columns.any { it.type is LosslessJdbcFieldType<*, *> }) {
                                log.warn {
                                    "fullRefreshTemporalColumn '$fullRefreshColName' not found in" +
                                        " SELECT columns for $key — date filtering skipped"
                                }
                            }
                            null
                        }
                        byName.type !is LosslessJdbcFieldType<*, *> -> null // discovery query
                        else -> byName
                    }
                }
                ast.orderBy is OrderBy -> (ast.orderBy as OrderBy).columns.firstOrNull()
                else -> null
            }
        if (cursorField == null) return ast

        // Build the extra date conditions using a LocalDate-typed binding
        val extra = mutableListOf<WhereClauseNode>()
        startDate?.let { extra += GreaterOrEqual(cursorField, LocalDateCodec.encode(it)) }
        endDate?.let { extra += LesserOrEqual(cursorField, LocalDateCodec.encode(it)) }

        fun addTo(w: WhereNode): WhereNode =
            when {
                extra.isEmpty() -> w
                w is NoWhere ->
                    Where(if (extra.size == 1) extra.first() else And(extra))
                w is Where -> Where(And(listOf(w.clause) + extra))
                else -> w
            }

        // For sampling queries, apply date conditions to the inner FromSample WHERE as well
        val newFrom =
            when (val f = ast.from) {
                is FromSample -> f.copy(where = addTo(f.where ?: NoWhere))
                else -> ast.from
            }
        return ast.copy(where = addTo(ast.where), from = newFrom)
    }

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
            is FromSample -> {
                val sample: String =
                    if (sampleRateInv == 1L) {
                        ""
                    } else {
                        " SAMPLE (${sampleRatePercentage.toPlainString()})"
                    }
                val innerFrom: String = From(name, namespace).sql() + sample
                val inner = "SELECT * $innerFrom ${where?.sql() ?: ""} ORDER BY RANDOM()"
                "FROM (SELECT * FROM ($inner) LIMIT $sampleSize)"
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

    fun SelectQuerySpec.bindings(): List<SelectQuery.Binding> =
        from.bindings() + where.bindings() + limit.bindings()

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

    override fun decorateRecordData(
        timestamp: OffsetDateTime,
        globalStateValue: OpaqueStateValue?,
        stream: Stream,
        recordData: NativeRecordPayload
    ) {
        return
    }
}
