/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.jdbc

import io.micronaut.context.annotation.ConfigurationProperties

const val JDBC_PROPERTY_PREFIX = "airbyte.connector.extract.jdbc"

@ConfigurationProperties(JDBC_PROPERTY_PREFIX)
data class DefaultJdbcConstants(
    val withSampling: Boolean = WITH_SAMPLING,
    val maxSampleSize: Int = TABLE_SAMPLE_SIZE,
    /** How many bytes per second we can expect the database to send to the connector. */
    val expectedThroughputBytesPerSecond: Long = THROUGHPUT_BYTES_PER_SECOND,
    /** Smallest possible fetchSize value. */
    val minFetchSize: Int = FETCH_SIZE_LOWER_BOUND,
    /** Default fetchSize value, in absence of any other estimate. */
    val defaultFetchSize: Int = DEFAULT_FETCH_SIZE,
    /** Largest possible fetchSize value. */
    val maxFetchSize: Int = FETCH_SIZE_UPPER_BOUND,
    /** How much of the JVM heap can we fill up with [java.sql.ResultSet] data. */
    val memoryCapacityRatio: Double = MEM_CAPACITY_RATIO,
    /**
     * Hard cap on the per-query [java.sql.ResultSet] buffer budget, in bytes. This caps the value
     * derived from [memoryCapacityRatio] / `maxConcurrency` so that a sample-based row-size
     * underestimate (e.g. a wide-row table whose tail rows are larger than anything in the sample)
     * cannot produce a fetchSize that, multiplied by the true row size, blows the heap.
     */
    val maxMemoryBytesPerQuery: Long = MAX_MEMORY_BYTES_PER_QUERY,
    /** Estimated bytes used as overhead for each row in a [java.sql.ResultSet]. */
    val estimatedRecordOverheadBytes: Long = RECORD_OVERHEAD_BYTES,
    /** Estimated bytes used as overhead for each column value in a [java.sql.ResultSet]. */
    val estimatedFieldOverheadBytes: Long = FIELD_OVERHEAD_BYTES,
    /** Overrides the JVM heap capacity to provide determinism in tests. */
    val maxMemoryBytesForTesting: Long? = null,
    /** Whether the namespace field denotes a JDBC schema or a JDBC catalog. */
    val namespaceKind: NamespaceKind = NamespaceKind.SCHEMA,
    val maxSequentialQueryLimit: Long? = MAX_SEQUENTIAL_QUERY_LIMIT_NULL,
    /** Whether to fetch pseudo-columns when querying column metadata. */
    val includePseudoColumns: Boolean = true,
    /** Namespaces to ignore when discovering all namespaces. */
    val ignoredNamespaces: Set<String> = emptySet(),
    /** Stream names to drop from the discovered catalog. */
    val ignoredStreams: Set<String> = emptySet(),
) {

    enum class NamespaceKind {
        SCHEMA,
        CATALOG,
        CATALOG_AND_SCHEMA
    }

    companion object {

        // Sampling defaults.
        const val WITH_SAMPLING: Boolean = false
        const val TABLE_SAMPLE_SIZE: Int = 1024
        const val THROUGHPUT_BYTES_PER_SECOND: Long = 10L shl 20

        // fetchSize defaults
        const val FETCH_SIZE_LOWER_BOUND: Int = 10
        const val DEFAULT_FETCH_SIZE: Int = 1_000
        const val FETCH_SIZE_UPPER_BOUND: Int = 10_000_000

        // Memory estimate defaults.
        const val RECORD_OVERHEAD_BYTES = 16L
        const val FIELD_OVERHEAD_BYTES = 16L
        // We're targeting use of 10% of the available memory for JDBC ResultSet buffering in
        // order to leave headroom for record processing, output framing, GC, and concurrent
        // partition readers. The legacy Java CDK uses the same 10% ratio (see
        // airbyte-cdk/java/.../FetchSizeConstants.kt). Multiplied by [MAX_MEMORY_BYTES_PER_QUERY],
        // this gives a defense-in-depth bound on per-query buffer demand.
        const val MEM_CAPACITY_RATIO: Double = 0.1
        // Hard cap on the per-query ResultSet buffer. The estimator divides the total memory
        // budget by `maxConcurrency`, but partition readers across streams may run
        // concurrently regardless of that configured value, and the row-size sample can
        // underestimate the tail. Capping per-query buffer at 500 MB matches the legacy Java CDK
        // fix and bounds total buffer demand to N_readers * 500 MB even when the per-query
        // share computed from `memoryCapacityRatio` is much larger.
        const val MAX_MEMORY_BYTES_PER_QUERY: Long = 500L shl 20 // 500 MiB
        val MAX_SEQUENTIAL_QUERY_LIMIT_NULL: Long? = null
    }
}
