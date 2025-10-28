/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.DefaultImplementation
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.PreparedStatement

/** Interface for executing delete queries against a database. */
@DefaultImplementation(JdbcDeleteQuerier::class)
interface DeleteQuerier {
    /**
     * Executes a DELETE query against the database.
     *
     * @param sql The SQL DELETE query to execute
     * @return The number of rows affected by the delete operation
     */
    fun executeDelete(
        sql: String,
    ): Int
}

/** Default implementation of [DeleteQuerier] for JDBC connections. */
@Singleton
class JdbcDeleteQuerier(private val jdbcConnectionFactory: JdbcConnectionFactory) : DeleteQuerier {
    private val log = KotlinLogging.logger {}

    override fun executeDelete(
        sql: String,
    ): Int {
        log.info { "Executing delete query: $sql" }
        var conn: Connection? = null
        var stmt: PreparedStatement? = null

        try {
            conn = jdbcConnectionFactory.get()
            conn.isReadOnly = false
            stmt = conn.prepareStatement(sql)

            // Execute the delete statement and return the count of affected rows
            val rowsAffected: Int = stmt.executeUpdate()
            log.info { "Delete query affected $rowsAffected rows" }
            return rowsAffected
        } finally {
            try {
                stmt?.close()
            } finally {
                conn?.close()
            }
        }
    }
}
