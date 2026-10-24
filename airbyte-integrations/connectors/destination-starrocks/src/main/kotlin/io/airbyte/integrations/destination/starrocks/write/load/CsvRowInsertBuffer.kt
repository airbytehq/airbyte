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
import io.airbyte.integrations.destination.starrocks.http.StreamLoadClient
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.security.MessageDigest
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

private val log = KotlinLogging.logger {}

/**
 * Accumulates records as CSV and ships them to a StarRocks table via Stream Load. Encapsulates the
 * StarRocks-specific buffering/serialization, separate from the CDK loader state machine (the
 * StarRocks analogue of ClickHouse's `BinaryRowInsertBuffer`).
 *
 * CSV is escaped per StarRocks Stream Load defaults: `column_separator=,`, fields enclosed in `"`
 * with internal `"` doubled, and SQL NULL written as `\N`.
 *
 * For Dedupe streams carrying CDC, a trailing `__op` column is appended: `1` (delete) when
 * `_ab_cdc_deleted_at` is present on the record, else `0` (upsert). StarRocks then applies the
 * delete/upsert against the PRIMARY KEY table at load time.
 */
class CsvRowInsertBuffer(
    val tableName: TableName,
    /** Final columns, in the order they appear in CSV rows and the `columns` Stream Load header. */
    private val columns: List<String>,
    /** True for Dedupe streams whose schema includes the CDC `_ab_cdc_deleted_at` column. */
    private val cdcDeleteEnabled: Boolean,
    private val streamLoadClient: StreamLoadClient,
    /**
     * Soft-delete mode: keep CDC-deleted rows (upsert with `__op=0`) instead of removing them, so
     * the `_ab_cdc_deleted_at` tombstone is retained in the PRIMARY KEY table.
     */
    private val softDelete: Boolean = false,
) : RowInsertBuffer {
    private val csv = ByteArrayOutputStream()
    private var rowCount = 0L

    /** Appends one CSV row built from [recordFields], keyed by final column name. */
    override fun accumulate(recordFields: Map<String, AirbyteValue>) {
        val row = StringBuilder()
        columns.forEachIndexed { i, column ->
            if (i > 0) row.append(COLUMN_SEPARATOR)
            row.append(renderCell(recordFields[column] ?: NullValue))
        }
        if (cdcDeleteEnabled) {
            row.append(COLUMN_SEPARATOR).append(opValue(recordFields[CDC_DELETED_AT_COLUMN]))
        }
        row.append(ROW_DELIMITER)
        csv.write(row.toString().toByteArray(Charsets.UTF_8))
        rowCount++
    }

    /** Current accumulated CSV (for tests/diagnostics). */
    internal fun csvSnapshot(): String = csv.toString(Charsets.UTF_8)

    /** Builds the comma-joined `columns` header for the Stream Load request. */
    fun columnsHeader(): String =
        if (cdcDeleteEnabled) {
            (columns + OP_COLUMN).joinToString(",")
        } else {
            columns.joinToString(",")
        }

    /**
     * Stream Load request headers. HTTP header values MUST NOT contain control characters, so the
     * row delimiter is intentionally NOT sent: StarRocks defaults to `\n`, which is exactly what
     * the CSV body uses. (Sending `row_delimiter: \n` makes OkHttp reject the header with
     * "Unexpected char 0x0a".) Likewise we rely on `enclose` + doubled quotes for escaping rather
     * than an `escape` char, to avoid colliding with the `\N` null marker.
     */
    internal fun streamLoadHeaders(): Map<String, String> =
        mapOf(
            "format" to "CSV",
            "column_separator" to COLUMN_SEPARATOR,
            "enclose" to "\"",
            "columns" to columnsHeader(),
        )

    override suspend fun flush() {
        if (rowCount == 0L) {
            log.info { "No rows to flush for ${tableName.name}; skipping Stream Load" }
            return
        }
        val body = csv.toByteArray()
        // Content-addressed label so a retry of the SAME batch is idempotent: every record carries
        // a
        // unique `_airbyte_raw_id`, so the CSV body (and its hash) is unique per distinct batch but
        // byte-identical across retries of that batch. StarRocks then rejects the re-load with
        // "Label Already Exists", which we treat as success — preventing duplicate rows on retry
        // (#40).
        val label = streamLoadLabel(body)
        val headers = streamLoadHeaders()

        log.info { "Stream Load of $rowCount rows into ${tableName.namespace}.${tableName.name}" }
        val response =
            streamLoadClient.streamLoad(
                database = tableName.namespace,
                table = tableName.name,
                label = label,
                headers = headers,
                body = body,
            )
        if (!response.isSuccess && !response.labelAlreadyExists) {
            throw RuntimeException(
                "Stream Load into ${tableName.namespace}.${tableName.name} failed " +
                    "(status=${response.status}, message=${response.message}, errorUrl=${response.errorUrl})",
            )
        }
        if (response.labelAlreadyExists) {
            log.info {
                "Stream Load label $label already committed — treating as success (idempotent retry)"
            }
        } else {
            log.info { "Stream Load finished: ${response.loadedRows} rows into ${tableName.name}" }
        }
    }

    /**
     * `__op` cell: 1 (delete) when the CDC deleted-at value is present, else 0 (upsert). In
     * soft-delete mode we always upsert (0), retaining the deleted row with its tombstone column.
     */
    private fun opValue(deletedAt: AirbyteValue?): String =
        if (!softDelete && deletedAt != null && deletedAt !is NullValue) DELETE_OP else UPSERT_OP

    private fun renderCell(value: AirbyteValue): String =
        when (value) {
            is NullValue -> NULL_MARKER
            is StringValue -> quote(value.value)
            is IntegerValue -> value.value.toString()
            is NumberValue -> value.value.toString()
            is BooleanValue -> if (value.value) "1" else "0"
            is DateValue -> value.value.toString()
            is TimeWithTimezoneValue -> value.value.toString()
            is TimeWithoutTimezoneValue -> value.value.toString()
            // StarRocks DATETIME wants `yyyy-MM-dd HH:mm:ss` (space, no `T`/`Z`). `toString()`
            // emits
            // ISO-8601 with a `T` (and trailing offset for tz-aware), which relies on lenient
            // parsing
            // and drops the offset. Format explicitly; normalize tz-aware values to UTC first
            // (#34).
            is TimestampWithTimezoneValue ->
                value.value.withOffsetSameInstant(ZoneOffset.UTC).format(SR_DATETIME)
            is TimestampWithoutTimezoneValue -> value.value.format(SR_DATETIME)
            is ObjectValue -> quote(value.values.serializeToString())
            is ArrayValue -> quote(value.values.serializeToString())
        }

    /**
     * Encloses a field in `"` and doubles any internal `"` (StarRocks `enclose`/`escape` default).
     */
    private fun quote(raw: String): String = "\"" + raw.replace("\"", "\"\"") + "\""

    /**
     * Content-addressed Stream Load label: stable across retries of the same batch (identical body,
     * since each record carries a unique `_airbyte_raw_id`) and distinct across different batches.
     */
    internal fun streamLoadLabel(body: ByteArray): String =
        "airbyte-${tableName.name.take(48)}-${sha256Hex(body)}"

    private fun sha256Hex(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    companion object {
        /** StarRocks DATETIME literal format (space-separated, no `T`/timezone). */
        private val SR_DATETIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
        const val COLUMN_SEPARATOR = ","
        const val ROW_DELIMITER = "\n"
        const val NULL_MARKER = "\\N"
        const val OP_COLUMN = "__op"
        const val UPSERT_OP = "0"
        const val DELETE_OP = "1"
    }
}
