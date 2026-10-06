/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.load

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.github.luben.zstd.ZstdOutputStream
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
import io.airbyte.integrations.destination.starrocks.spec.LoadCompression
import io.airbyte.integrations.destination.starrocks.write.load.CsvRowInsertBuffer.Companion.OP_COLUMN
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.security.MessageDigest
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.util.zip.GZIPOutputStream

private val log = KotlinLogging.logger {}

/**
 * JSON variant of [CsvRowInsertBuffer]. Ships records as a JSON array Stream Load (`format=json`,
 * `strip_outer_array=true`). Chosen over CSV when correctness matters more than raw throughput:
 * - No CSV escaping ambiguity. In particular a literal `\N` string round-trips (CSV stores it as
 * NULL because StarRocks' CSV null marker is `\N` even inside an enclosure).
 * - Integers and decimals are emitted as JSON **strings** so large BIGINT/DECIMAL values keep full
 * precision (a JSON number would be parsed as a double and lose/overflow precision).
 *
 * For Dedupe+CDC streams a numeric `__op` field is added (`1` delete / `0` upsert), the same
 * load-time PRIMARY KEY semantics the CSV path uses.
 */
class JsonRowInsertBuffer(
    val tableName: TableName,
    private val columns: List<String>,
    private val cdcDeleteEnabled: Boolean,
    private val streamLoadClient: StreamLoadClient,
    private val softDelete: Boolean = false,
    /**
     * Request-body compression algorithm ("gzip" / "zstd"), or null for none. Sends the compressed
     * body with a `compression: <algo>` header. Only set when the cluster supports request-body
     * compression (>= 3.3.2); StarRocks honors it for JSON Stream Load only.
     */
    private val compression: String? = null,
) : RowInsertBuffer {
    private val mapper = ObjectMapper()
    private val rows: ArrayNode = mapper.createArrayNode()

    override fun accumulate(recordFields: Map<String, AirbyteValue>) {
        val obj = mapper.createObjectNode()
        columns.forEach { column -> putCell(obj, column, recordFields[column] ?: NullValue) }
        if (cdcDeleteEnabled) {
            obj.put(OP_COLUMN, opValue(recordFields[CDC_DELETED_AT_COLUMN]))
        }
        rows.add(obj)
    }

    /** Current accumulated JSON body (for tests/diagnostics). */
    internal fun bodySnapshot(): ByteArray = mapper.writeValueAsBytes(rows)

    /** `columns` header so StarRocks maps JSON keys (incl. `__op`) to table columns by name. */
    internal fun columnsHeader(): String =
        if (cdcDeleteEnabled) (columns + OP_COLUMN).joinToString(",") else columns.joinToString(",")

    internal fun streamLoadHeaders(): Map<String, String> =
        mapOf(
            "format" to "JSON",
            "strip_outer_array" to "true",
            "columns" to columnsHeader(),
        )

    internal fun streamLoadLabel(body: ByteArray): String =
        "airbyte-${tableName.name.take(48)}-${sha256Hex(body)}"

    override suspend fun flush() {
        if (rows.isEmpty) {
            log.info { "No rows to flush for ${tableName.name}; skipping Stream Load" }
            return
        }
        val rawBody = mapper.writeValueAsBytes(rows)
        // Label is content-addressed on the UNCOMPRESSED body so a batch's identity (hence
        // idempotent
        // retry — #40) is independent of whether/how it was compressed.
        val label = streamLoadLabel(rawBody)
        val body = if (compression != null) compress(compression, rawBody) else rawBody
        val headers =
            if (compression != null) streamLoadHeaders() + ("compression" to compression)
            else streamLoadHeaders()

        log.info {
            val how =
                if (compression != null) "JSON, $compression ${rawBody.size}->${body.size}B"
                else "JSON"
            "Stream Load ($how) of ${rows.size()} rows into ${tableName.namespace}.${tableName.name}"
        }
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
        }
    }

    /**
     * `__op` value: 1 (delete) when CDC deleted-at is present and not soft-delete, else 0 (upsert).
     */
    private fun opValue(deletedAt: AirbyteValue?): Int =
        if (!softDelete && deletedAt != null && deletedAt !is NullValue) 1 else 0

    private fun putCell(obj: ObjectNode, column: String, value: AirbyteValue) {
        when (value) {
            is NullValue -> obj.putNull(column)
            is StringValue -> obj.put(column, value.value)
            // Numbers as STRINGS: a JSON number would be parsed as a double, losing precision and
            // overflowing on large BIGINT/DECIMAL. StarRocks casts the string to the column type.
            is IntegerValue -> obj.put(column, value.value.toString())
            is NumberValue -> obj.put(column, value.value.toString())
            is BooleanValue -> obj.put(column, value.value)
            is DateValue -> obj.put(column, value.value.toString())
            is TimeWithTimezoneValue -> obj.put(column, value.value.toString())
            is TimeWithoutTimezoneValue -> obj.put(column, value.value.toString())
            is TimestampWithTimezoneValue ->
                obj.put(
                    column,
                    value.value.withOffsetSameInstant(ZoneOffset.UTC).format(SR_DATETIME)
                )
            is TimestampWithoutTimezoneValue -> obj.put(column, value.value.format(SR_DATETIME))
            // Objects/arrays serialize to a JSON string — works for both STRING columns and
            // StarRocks
            // JSON columns (which parse the string), matching the CSV path's behavior.
            is ObjectValue -> obj.put(column, value.values.serializeToString())
            is ArrayValue -> obj.put(column, value.values.serializeToString())
        }
    }

    private fun sha256Hex(bytes: ByteArray): String =
        MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    /**
     * Compress the request body with the requested algorithm (gzip is JVM-built-in; zstd via
     * zstd-jni). Idempotency is unaffected: the retry label is content-addressed on the
     * uncompressed body.
     */
    internal fun compress(algo: String, data: ByteArray): ByteArray {
        val baos = ByteArrayOutputStream(data.size / 2)
        val out: OutputStream =
            when (algo) {
                LoadCompression.GZIP -> GZIPOutputStream(baos)
                LoadCompression.ZSTD -> ZstdOutputStream(baos)
                else -> throw IllegalArgumentException("Unsupported compression algorithm: $algo")
            }
        out.use { it.write(data) }
        return baos.toByteArray()
    }

    companion object {
        private val SR_DATETIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
    }
}
