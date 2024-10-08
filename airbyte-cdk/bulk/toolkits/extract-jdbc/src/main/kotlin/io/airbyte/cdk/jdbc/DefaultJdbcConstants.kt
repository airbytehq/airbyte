/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
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
    /** Estimated bytes used as overhead for each row in a [java.sql.ResultSet]. */
    val estimatedRecordOverheadBytes: Long = RECORD_OVERHEAD_BYTES,
    /** Estimated bytes used as overhead for each column value in a [java.sql.ResultSet]. */
    val estimatedFieldOverheadBytes: Long = FIELD_OVERHEAD_BYTES,
    /** Overrides the JVM heap capacity to provide determinism in tests. */
    val maxMemoryBytesForTesting: Long? = null,
    /** Whether the namespace field denotes a JDBC schema or a JDBC catalog. */
    val namespaceKind: NamespaceKind = NamespaceKind.SCHEMA,
) {

    enum class NamespaceKind {
        SCHEMA,
        CATALOG,
        CATALOG_AND_SCHEMA
    }

    companion object {

        // Sampling defaults.
        internal const val WITH_SAMPLING: Boolean = false
        internal const val TABLE_SAMPLE_SIZE: Int = 1024
        internal const val THROUGHPUT_BYTES_PER_SECOND: Long = 10L shl 20

        // fetchSize defaults
        internal const val FETCH_SIZE_LOWER_BOUND: Int = 10
        internal const val DEFAULT_FETCH_SIZE: Int = 1_000
        internal const val FETCH_SIZE_UPPER_BOUND: Int = 10_000_000

        // Memory estimate defaults.
        internal const val RECORD_OVERHEAD_BYTES = 16L
        internal const val FIELD_OVERHEAD_BYTES = 16L
        // We're targeting use of 60% of the available memory in order to allow
        // for some headroom for other garbage collection.
        internal const val MEM_CAPACITY_RATIO: Double = 0.6
    }
}
