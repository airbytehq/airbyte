/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.test.fixtures.connector

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.SQLException
import java.util.function.Supplier

class JdbcTestDbExecutor(
    override val assetName: String,
    jdbcConfig: JdbcSourceConfiguration,
) : TestDbExecutor {

    private val log = KotlinLogging.logger {}
    private val connectionFactory: Supplier<Connection> = JdbcConnectionFactory(jdbcConfig)
    private var connection: Connection? = null

    override fun executeReadQuery(query: String): List<Map<String, Any?>> {
        log.info { "Executing read query: $query" }
        ensureConnection().createStatement().use { statement ->
            statement.executeQuery(query).use { resultSet ->
                val metaData = resultSet.metaData
                val columnCount = metaData.columnCount

                val rows: MutableList<Map<String, Any?>> = mutableListOf()

                while (resultSet.next()) {
                    val row = mutableMapOf<String, Any?>()
                    for (i in 1..columnCount) {
                        row[metaData.getColumnName(i)] = resultSet.getObject(i)
                    }
                    rows.add(row)
                }

                return rows
            }
        }
    }

    override fun executeUpdate(query: String) {
        log.info { "Executing update query: $query" }
        ensureConnection().createStatement().use { statement -> statement.executeUpdate(query) }
    }

    override fun close() {
        try {
            connection?.close()
        } catch (e: SQLException) {
            log.warn { "Failed to close database connection: ${e.message}" }
        }
    }

    private fun ensureConnection(): Connection {
        if (connection == null || connection!!.isClosed) {
            connection = connectionFactory.get()
        }
        return connection!!
    }
}
