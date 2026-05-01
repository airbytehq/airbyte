/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.annotation.PreDestroy
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.DriverManager
import java.sql.ShardingKey
import java.time.Duration
import java.util.Properties
import org.postgresql.PGConnection
import org.postgresql.util.PSQLException

@Singleton
@Primary
class PostgresSourceJdbcConnectionFactory(pgConfig: PostgresSourceConfiguration) :
    JdbcConnectionFactory(pgConfig) {
    private val log = KotlinLogging.logger {}
    private val maxConcurrency: Int = pgConfig.maxConcurrency

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

    private val _dataSourceLazy = lazy { createDataSource() }
    private val dataSource: HikariDataSource by _dataSourceLazy

    private fun createDataSource(): HikariDataSource {
        val tunnelSession: TunnelSession = ensureTunnelSession()
        val jdbcUrl =
            String.format(
                config.jdbcUrlFmt,
                tunnelSession.address.hostName,
                tunnelSession.address.port,
            )
        log.info { "Creating HikariCP connection pool with size ${maxConcurrency + 1}." }
        return HikariDataSource(
            HikariConfig().apply {
                this.jdbcUrl = jdbcUrl
                isAutoCommit = false
                maximumPoolSize = maxConcurrency + 1
                minimumIdle = 0
                keepaliveTime = Duration.ofSeconds(30).toMillis()
                maxLifetime = Duration.ofMinutes(30).toMillis()
                connectionTimeout = Duration.ofSeconds(30).toMillis()
                dataSourceProperties = Properties().apply { putAll(config.jdbcProperties) }
            }
        )
    }

    override fun get(): Connection = ConnectionWithCleanup(dataSource.connection)

    private class ConnectionWithCleanup(val base: Connection) : Connection by base {
        // prevents closing the socket with an open transaction which causes problems with poolers
        override fun close() {
            base.use { it.rollback() }
        }

        // below are boilerplate - Java class requires explicit delegation on default methods
        override fun beginRequest() {
            base.beginRequest()
        }
        override fun endRequest() {
            base.endRequest()
        }
        override fun setShardingKeyIfValid(
            shardingKey: ShardingKey?,
            superShardingKey: ShardingKey?,
            timeout: Int
        ): Boolean {
            return base.setShardingKeyIfValid(shardingKey, superShardingKey, timeout)
        }
        override fun setShardingKeyIfValid(shardingKey: ShardingKey?, timeout: Int): Boolean {
            return base.setShardingKeyIfValid(shardingKey, timeout)
        }
        override fun setShardingKey(shardingKey: ShardingKey?, superShardingKey: ShardingKey?) {
            base.setShardingKey(shardingKey, superShardingKey)
        }
        override fun setShardingKey(shardingKey: ShardingKey?) {
            base.setShardingKey(shardingKey)
        }
    }

    @PreDestroy
    fun close() {
        if (_dataSourceLazy.isInitialized()) dataSource.close()
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
