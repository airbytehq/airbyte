/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.integration

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

object MysqlTestDestinationCleaner : DestinationCleaner {
    override fun cleanup() {
        // For now, we don't need to clean up old test data in MySQL
        // This is typically used for CI environments to clean up old test schemas
        // If needed, we can read the config from a file like Snowflake does
        return
    }

    fun cleanupWithSpec(spec: ConfigurationSpecification) {
        val mysqlSpec = spec as MysqlSpecification
        val dataSource = createDataSource(mysqlSpec)

        dataSource.connection.use { connection ->
            // Get all databases (schemas) that match the test pattern
            val sql = """
                SELECT SCHEMA_NAME
                FROM INFORMATION_SCHEMA.SCHEMATA
                WHERE SCHEMA_NAME LIKE 'test_%'
            """.trimIndent()

            connection.createStatement().use { statement ->
                val schemasToDelete = mutableListOf<String>()

                statement.executeQuery(sql).use { resultSet ->
                    while (resultSet.next()) {
                        schemasToDelete.add(resultSet.getString("SCHEMA_NAME"))
                    }
                }

                // Drop each test schema
                schemasToDelete.forEach { schema ->
                    try {
                        log.info { "Dropping test schema: $schema" }
                        statement.execute("DROP DATABASE IF EXISTS `$schema`")
                    } catch (e: Exception) {
                        log.warn(e) { "Failed to drop schema $schema" }
                    }
                }
            }
        }
    }

    private fun createDataSource(spec: MysqlSpecification): DataSource {
        val baseUrl = "jdbc:mysql://${spec.host}:${spec.port}/${spec.database}"
        val sslParam = if (spec.ssl) {
            "sslMode=${spec.sslMode?.value ?: "PREFERRED"}"
        } else {
            "sslMode=DISABLED"
        }
        val jdbcUrl = if (spec.jdbcUrlParams.isNullOrBlank()) {
            "$baseUrl?$sslParam"
        } else {
            "$baseUrl?$sslParam&${spec.jdbcUrlParams}"
        }

        val config = HikariConfig().apply {
            this.jdbcUrl = jdbcUrl
            username = spec.username
            password = spec.password
            driverClassName = "com.mysql.cj.jdbc.Driver"
            maximumPoolSize = 2
        }

        return HikariDataSource(config)
    }
}
