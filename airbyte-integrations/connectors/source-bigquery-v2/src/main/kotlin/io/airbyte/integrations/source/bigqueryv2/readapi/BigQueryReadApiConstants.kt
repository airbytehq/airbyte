/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import io.micronaut.context.annotation.ConfigurationProperties

const val BIGQUERY_READ_API_PROPERTY_PREFIX = "airbyte.connector.extract.bigquery"

/**
 * Tuning knobs of the Storage Read API read path, bound from `application.yml` under
 * [BIGQUERY_READ_API_PROPERTY_PREFIX].
 */
@ConfigurationProperties(BIGQUERY_READ_API_PROPERTY_PREFIX)
data class BigQueryReadApiConstants(
    /**
     * Target logical size of one read stream, in bytes. A table is split into `ceil(numBytes /
     * readStreamTargetBytes)` read streams (at least the connector's concurrency, at most
     * [maxReadStreams]); each completed read stream advances the checkpoint, so smaller read
     * streams mean finer-grained progress and less work redone after a failure.
     */
    val readStreamTargetBytes: Long = DEFAULT_READ_STREAM_TARGET_BYTES,
    /** Upper bound on the read streams requested for one table; the API caps at 1,000. */
    val maxReadStreams: Int = DEFAULT_MAX_READ_STREAMS,
    /**
     * Arrow buffer compression requested from the API: `NONE`, `LZ4_FRAME` or `ZSTD`. Compression
     * trades connector CPU for network bytes; the BigQuery side keeps up either way. `ZSTD`
     * (zstd-jni, native) measured both faster and cheaper in CPU than `LZ4_FRAME`
     * (commons-compress, pure Java): 5.22M rows at concurrency 4 took 29 s uncompressed, 21 s with
     * LZ4 at 265% CPU, 17 s with ZSTD at 96% CPU.
     */
    val arrowBufferCompression: String = DEFAULT_ARROW_BUFFER_COMPRESSION,
    /**
     * How long a `ReadRows` call may go without delivering a message before it is failed (and the
     * read stream resumed at its offset by the next attempt), so a dead read stream cannot hang a
     * sync forever.
     */
    val readRowsIdleTimeoutSeconds: Long = DEFAULT_READ_ROWS_IDLE_TIMEOUT_SECONDS,
    /**
     * Target logical size of one partition on the JDBC fallback path (used when the Storage Read
     * API is off or not permitted). A base table with a single quantile-friendly primary key is
     * split into `ceil(numBytes / fallbackPartitionTargetBytes)` key ranges (at most
     * [fallbackMaxPartitions]), whose boundaries come from `APPROX_QUANTILES` over the key column.
     * Each range is still a full-table scan on BigQuery unless the table is clustered or
     * partitioned on the key, so this trades bytes billed for checkpoint granularity; 32 GiB keeps
     * the number of rescans low.
     */
    val fallbackPartitionTargetBytes: Long = DEFAULT_FALLBACK_PARTITION_TARGET_BYTES,
    /**
     * Target number of rows per partition, used only when the table does not report `numBytes` (the
     * BigQuery emulator, and any table BigQuery has not sized yet). Keeps the fallback splittable
     * for such tables; the real service always reports `numBytes`, so
     * [fallbackPartitionTargetBytes] governs there.
     */
    val fallbackPartitionTargetRows: Long = DEFAULT_FALLBACK_PARTITION_TARGET_ROWS,
    /** Upper bound on the number of key ranges the fallback path splits a table into. */
    val fallbackMaxPartitions: Int = DEFAULT_FALLBACK_MAX_PARTITIONS,
) {
    companion object {
        const val DEFAULT_READ_ROWS_IDLE_TIMEOUT_SECONDS: Long = 600L
        const val DEFAULT_READ_STREAM_TARGET_BYTES: Long = 8L shl 30
        const val DEFAULT_MAX_READ_STREAMS: Int = 1_000
        const val DEFAULT_ARROW_BUFFER_COMPRESSION: String = "ZSTD"
        const val DEFAULT_FALLBACK_PARTITION_TARGET_BYTES: Long = 32L shl 30
        const val DEFAULT_FALLBACK_PARTITION_TARGET_ROWS: Long = 50_000_000L
        const val DEFAULT_FALLBACK_MAX_PARTITIONS: Int = 1_000
    }
}
