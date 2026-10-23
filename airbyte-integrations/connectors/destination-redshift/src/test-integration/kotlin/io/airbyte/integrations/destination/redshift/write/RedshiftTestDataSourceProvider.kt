/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.write

import com.zaxxer.hikari.HikariDataSource
import io.airbyte.integrations.destination.redshift.connect.RedshiftConnect
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

/** Provides a single shared [HikariDataSource] for all integration tests */
class RedshiftTestDataSourceProvider private constructor() {
    companion object {
        @Volatile private var dataSource: HikariDataSource? = null

        fun get(): HikariDataSource {
            return dataSource
                ?: synchronized(this) {
                    dataSource
                        ?: run {
                            val config = RedshiftTestConfigProvider.configFromFile()
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
