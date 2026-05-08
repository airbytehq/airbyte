/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import kotlin.test.assertEquals
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

internal class MSSQLConfigurationTest {

    private val config =
        MSSQLConfiguration(
            host = "localhost",
            port = 1433,
            database = "master",
            schema = "dbo",
            user = "airbyte",
            password = "password",
            jdbcUrlParams = null,
            sslMethod = Unencrypted(),
            ssh = null,
            mssqlLoadTypeConfiguration = MSSQLLoadTypeConfiguration(InsertLoadTypeConfiguration()),
        )

    @Test
    fun `recordBatchSizeBytes is 5MB to limit per-loader memory`() {
        val fiveMB = 5L * 1024 * 1024
        assertEquals(fiveMB, config.recordBatchSizeBytes)
    }

    @Test
    fun `maxBatchSizeBytes equals recordBatchSizeBytes`() {
        assertEquals(config.recordBatchSizeBytes, config.maxBatchSizeBytes)
    }

    @Test
    fun `batchEveryNRecords is 2500 for more frequent JDBC flushes`() {
        assertEquals(2_500, config.batchEveryNRecords)
    }

    @Test
    fun `maxNumOpenLoaders is 4 to reduce concurrent memory usage`() {
        assertEquals(4, config.maxNumOpenLoaders)
    }

    @Test
    fun `peak theoretical memory from loaders is bounded`() {
        // With 4 loaders each holding up to 5MB, peak is 20MB.
        // Previous settings (8 loaders x 10MB) allowed 80MB.
        val peakBytes = config.maxNumOpenLoaders.toLong() * config.recordBatchSizeBytes
        assertTrue(
            peakBytes <= 25L * 1024 * 1024,
            "Peak loader memory should be <= 25MB, was $peakBytes"
        )
    }
}
