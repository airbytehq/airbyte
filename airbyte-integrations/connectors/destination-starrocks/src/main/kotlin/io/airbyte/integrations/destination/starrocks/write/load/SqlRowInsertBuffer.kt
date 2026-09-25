/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.starrocks.sql.quoteIdent
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.DriverManager
import java.sql.Types
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

private val log = KotlinLogging.logger {}

/**
 * SQL load path (issue #68): instead of HTTP Stream Load, ships records over the (possibly
 * tunneled, possibly TLS) **JDBC connection** with batched `INSERT` / `DELETE`. Lower throughput
 * than Stream Load, but it traverses an SSH tunnel and end-to-end SSL cleanly — Stream Load's HTTP
 * data plane does neither.
 *
 * - Append / Overwrite (DUPLICATE KEY) and Dedup upserts → `INSERT` (a StarRocks PRIMARY KEY table
 * upserts on insert by key).
 * - CDC hard-delete → `DELETE FROM ... WHERE <pk> = ?` for the deleted keys. Soft-delete keeps
 * every row (the `_ab_cdc_deleted_at` tombstone is just inserted), so all rows are upserts.
 *
 * Every value is bound as a string (or SQL NULL) and StarRocks coerces it to the column type, which
 * preserves large BIGINT/DECIMAL precision (mirrors the JSON-as-strings Stream Load path).
 */
class SqlRowInsertBuffer(
    val tableName: TableName,
    private val columns: List<String>,
    private val cdcDeleteEnabled: Boolean,
    /** PRIMARY KEY columns, used to build CDC `DELETE` predicates. Empty for non-dedup streams. */
    private val primaryKeyColumns: List<String>,
    private val jdbcUrl: String,
    private val username: String,
    private val password: String,
    private val softDelete: Boolean = false,
) : RowInsertBuffer {

    private val rows = mutableListOf<Map<String, AirbyteValue>>()

    override fun accumulate(recordFields: Map<String, AirbyteValue>) {
        rows.add(recordFields)
    }

    /** Whether a record is a CDC hard-delete (deleted-at present, and not soft-delete mode). */
    private fun isDelete(record: Map<String, AirbyteValue>): Boolean {
        if (!cdcDeleteEnabled || softDelete) return false
        val deletedAt = record[CDC_DELETED_AT_COLUMN]
        return deletedAt != null && deletedAt !is NullValue
    }

    internal fun insertSql(): String {
        val cols = columns.joinToString(", ") { quoteIdent(it) }
        val placeholders = columns.joinToString(", ") { "?" }
        return "INSERT INTO ${quoteIdent(tableName.namespace)}.${quoteIdent(tableName.name)} ($cols) VALUES ($placeholders)"
    }

    internal fun deleteSql(): String {
        val predicate = primaryKeyColumns.joinToString(" AND ") { "${quoteIdent(it)} = ?" }
        return "DELETE FROM ${quoteIdent(tableName.namespace)}.${quoteIdent(tableName.name)} WHERE $predicate"
    }

    override suspend fun flush() {
        if (rows.isEmpty()) {
            log.info { "No rows to flush for ${tableName.name}; skipping SQL load" }
            return
        }
        val (upserts, deletes) = resolveOperations()

        DriverManager.getConnection(jdbcUrl, username, password).use { conn ->
            conn.autoCommit = false
            if (upserts.isNotEmpty()) batchInsert(conn, upserts)
            if (deletes.isNotEmpty()) batchDelete(conn, deletes)
            conn.commit()
        }
        log.info {
            "SQL load into ${tableName.namespace}.${tableName.name}: ${upserts.size} upserts" +
                if (deletes.isNotEmpty()) ", ${deletes.size} deletes" else ""
        }
        rows.clear()
    }

    /**
     * Resolve the buffered records into (rows to upsert, rows to delete).
     *
     * For a CDC hard-delete stream the records are collapsed to the **last event per primary key in
     * arrival order**, so a `delete(K)` followed by an `insert(K)` in the same flush ends as an
     * upsert (and an `insert(K)` followed by `delete(K)` ends as a delete). Without this, splitting
     * the batch into "all upserts then all deletes" would run the INSERT before the DELETE and drop
     * a row that should exist — diverging from the order-preserving Stream Load path. Collapsing by
     * key also makes the upsert/delete sets disjoint, so executing inserts before deletes is safe.
     *
     * Non-CDC-delete streams keep every row: StarRocks PRIMARY KEY tables upsert on load (last
     * write wins) and DUPLICATE KEY / append tables want every row, so no collapsing is applied.
     */
    internal fun resolveOperations():
        Pair<List<Map<String, AirbyteValue>>, List<Map<String, AirbyteValue>>> {
        if (!cdcDeleteEnabled || softDelete || rows.none { isDelete(it) })
            return rows.toList() to emptyList()
        // Degenerate: CDC delete with no key to dedup/target — fall back to a plain partition.
        if (primaryKeyColumns.isEmpty())
            return rows.filterNot { isDelete(it) } to rows.filter { isDelete(it) }

        val lastByKey = LinkedHashMap<List<String?>, Map<String, AirbyteValue>>()
        for (record in rows) {
            lastByKey[primaryKeyColumns.map { sqlString(record[it] ?: NullValue) }] = record
        }
        val resolved = lastByKey.values.toList()
        return resolved.filterNot { isDelete(it) } to resolved.filter { isDelete(it) }
    }

    private fun batchInsert(conn: Connection, batch: List<Map<String, AirbyteValue>>) {
        conn.prepareStatement(insertSql()).use { ps ->
            batch.chunked(MAX_ROWS_PER_STATEMENT).forEach { chunk ->
                chunk.forEach { record ->
                    columns.forEachIndexed { i, column ->
                        when (val s = sqlString(record[column] ?: NullValue)) {
                            null -> ps.setNull(i + 1, Types.VARCHAR)
                            else -> ps.setString(i + 1, s)
                        }
                    }
                    ps.addBatch()
                }
                ps.executeBatch()
            }
        }
    }

    private fun batchDelete(conn: Connection, batch: List<Map<String, AirbyteValue>>) {
        conn.prepareStatement(deleteSql()).use { ps ->
            batch.chunked(MAX_ROWS_PER_STATEMENT).forEach { chunk ->
                chunk.forEach { record ->
                    primaryKeyColumns.forEachIndexed { i, pk ->
                        when (val s = sqlString(record[pk] ?: NullValue)) {
                            null -> ps.setNull(i + 1, Types.VARCHAR)
                            else -> ps.setString(i + 1, s)
                        }
                    }
                    ps.addBatch()
                }
                ps.executeBatch()
            }
        }
    }

    /** Value as a string StarRocks coerces to the column type, or null for SQL NULL. */
    internal fun sqlString(value: AirbyteValue): String? =
        when (value) {
            is NullValue -> null
            is StringValue -> value.value
            is IntegerValue -> value.value.toString()
            is NumberValue -> value.value.toString()
            is BooleanValue -> if (value.value) "1" else "0"
            is DateValue -> value.value.toString()
            is TimeWithTimezoneValue -> value.value.toString()
            is TimeWithoutTimezoneValue -> value.value.toString()
            is TimestampWithTimezoneValue ->
                value.value.withOffsetSameInstant(ZoneOffset.UTC).format(SR_DATETIME)
            is TimestampWithoutTimezoneValue -> value.value.format(SR_DATETIME)
            is ObjectValue -> value.values.serializeToString()
            is ArrayValue -> value.values.serializeToString()
        }

    companion object {
        private val SR_DATETIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")

        // StarRocks FE rejects a multi-row INSERT with more rows than its `expr_children_limit`
        // (default 10000), and `rewriteBatchedStatements` merges one executeBatch into one INSERT.
        // The dataflow aggregate holds up to 50k records, so execute in server-safe chunks.
        internal const val MAX_ROWS_PER_STATEMENT = 10_000
    }
}
