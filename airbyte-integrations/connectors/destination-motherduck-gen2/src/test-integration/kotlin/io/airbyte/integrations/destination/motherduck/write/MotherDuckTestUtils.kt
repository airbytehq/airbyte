/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.motherduck.write

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckConfiguration

object MotherDuckTestUtils {
    fun createDuckDBDataSource(config: MotherDuckConfiguration): HikariDataSource {
        val jdbcUrl = "jdbc:duckdb:${config.destinationPath}"
        val hikariConfig =
            HikariConfig().apply {
                driverClassName = "org.duckdb.DuckDBDriver"
                this.jdbcUrl = jdbcUrl
                maximumPoolSize = 5
                minimumIdle = 0
                idleTimeout = 60000L
                connectionTimeout = 10000L
                initializationFailTimeout = -1
            }
        return HikariDataSource(hikariConfig)
    }
}
