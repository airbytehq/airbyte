/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.DriverManager
import java.util.Properties
import org.postgresql.PGConnection
import org.postgresql.util.PSQLException

@Singleton
@Primary
class PostgresSourceJdbcConnectionFactory(pgConfig: PostgresSourceConfiguration) :
    JdbcConnectionFactory(pgConfig) {
    private val log = KotlinLogging.logger {}

    companion object {
        private const val USER = "user"
        private const val PASSWORD = "password"
    }

    val replicationProps: Map<String, String> =
        mapOf(
            "assumeMinServerVersion" to "9.4",
            "ApplicationName" to "Airbyte CDC Streaming",
            "replication" to "database",
            // replication protocol only supports simple query mode
            "preferQueryMode" to "simple",
            USER to config.jdbcProperties[USER]!!,
            PASSWORD to config.jdbcProperties[PASSWORD]!!,
        )

    override fun get(): Connection {
        // Setting autoCommit to false in pg jdbc allows the driver to start returning result before
        // the entire result set is received from the server. This improves performance and memory
        // consumption when fetching large result sets.
        return super.get().also { it.autoCommit = false }
    }

    fun getReplication(): PGConnection {
        val tunnelSession: TunnelSession = ensureTunnelSession()
        log.info { "Creating a replication connection." }
        val jdbcUrl: String =
            String.format(
                config.jdbcUrlFmt,
                tunnelSession.address.hostName,
                tunnelSession.address.port,
            )
        val props = Properties().apply { putAll(replicationProps) }

        val connection: Connection
        try {
            connection = DriverManager.getConnection(jdbcUrl, props)!!
        } catch (exception: PSQLException) {
            if ("42501" == exception.sqlState) { // insufficient_privilege
                throw ConfigErrorException(
                    "User '${replicationProps[USER]}' does not have sufficient privileges for " +
                        "CDC replication. Please read the docs and add required privileges."
                )
            }
            throw ConfigErrorException(
                "Unexpected failure while creating replication connection.",
                exception
            )
        }

        log.info { "Validating replication connection." }
        validateReplicationConnection(connection)

        return connection.unwrap(PGConnection::class.java)
    }

    private fun validateReplicationConnection(connection: Connection) {
        connection.createStatement().use { statement ->
            statement.executeQuery("IDENTIFY_SYSTEM").use { resultSet ->
                if (!resultSet!!.next()) {
                    throw ConfigErrorException(
                        "The DB connection is not a valid replication connection"
                    )
                }
            }
        }
    }
}
