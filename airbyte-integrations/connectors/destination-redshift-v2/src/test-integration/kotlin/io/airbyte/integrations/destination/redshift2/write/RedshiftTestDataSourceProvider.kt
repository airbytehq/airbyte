/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write

import com.zaxxer.hikari.HikariDataSource
import io.airbyte.integrations.destination.redshift2.connect.RedshiftConnect
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

/**
 * Provides a single shared [HikariDataSource] for all integration tests. This avoids the overhead
 * of creating and destroying a connection pool on every [RedshiftDataDumper.dumpRecords] or
 * [RedshiftDataCleaner.cleanup] call (~1-3 seconds of Redshift connection establishment each time).
 *
 * The DataSource is lazily initialized on first access and should be explicitly closed via [close]
 * in an `@AfterAll` method (see [RedshiftAcceptanceTest]).
 */
class RedshiftTestDataSourceProvider private constructor() {
    companion object {
        @Volatile private var dataSource: HikariDataSource? = null

        /**
         * Returns the shared [HikariDataSource], creating it on first access. Thread-safe via
         * double-checked locking.
         */
        fun get(): HikariDataSource {
            return dataSource
                ?: synchronized(this) {
                    dataSource
                        ?: run {
                            val config = loadConfig()
                            logger.info { "Creating shared test DataSource" }
                            RedshiftConnect(config).createDataSource().also { dataSource = it }
                        }
                }
        }

        /** Closes the shared [HikariDataSource] if it was initialized. */
        @Synchronized
        fun close() {
            dataSource?.let {
                logger.info { "Closing shared test DataSource" }
                it.close()
            }
            dataSource = null
        }
    }
}
