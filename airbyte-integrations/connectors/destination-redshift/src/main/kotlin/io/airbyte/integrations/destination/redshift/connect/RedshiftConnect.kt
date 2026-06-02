/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.startTunnelAndGetEndpoint
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlin.time.Duration.Companion.minutes

private val log = KotlinLogging.logger {}

/**
 * Manages Redshift JDBC connections with support for:
 * - HikariCP connection pooling
 * - SSL encryption (always enabled)
 * - SSH tunnel resolution (key-auth and password-auth)
 * - Configurable JDBC URL parameters
 */
@Singleton
class RedshiftConnect(
    private val configuration: RedshiftConfiguration,
) {

    /**
     * Resolves the database endpoint, tunneling through SSH if configured. When an SSH tunnel is
     * configured, this opens a local port-forward and returns the tunnel's local address.
     * Otherwise, the direct host/port is used.
     */
    fun resolveEndpoint(): String {
        val ssh = configuration.tunnelMethod ?: SshNoTunnelMethod
        return startTunnelAndGetEndpoint(ssh, configuration.host, configuration.port)
    }

    /** Creates a fully configured [HikariDataSource] for Redshift */
    fun createDataSource(): HikariDataSource {
        val endpoint = resolveEndpoint()
        val jdbcUrl = buildJdbcUrl(endpoint)

        log.info { "Creating Redshift DataSource for $endpoint/${configuration.database}" }

        val hikariConfig =
            HikariConfig().apply {
                connectionTimeout = 2.minutes.inWholeMilliseconds
                minimumIdle = 0
                initializationFailTimeout = -1
                this.jdbcUrl = jdbcUrl
                username = configuration.username
                password = configuration.password
                schema = configuration.schema

                addDataSourceProperty("ssl", "true")
                addDataSourceProperty("sslfactory", SSL_FACTORY)
            }

        return HikariDataSource(hikariConfig)
    }

    private fun buildJdbcUrl(endpoint: String): String =
        "jdbc:redshift://$endpoint/${configuration.database}" +
            (configuration.jdbcUrlParams?.takeIf { it.isNotBlank() }?.let { "?$it" } ?: "")

    companion object {
        const val SSL_FACTORY = "com.amazon.redshift.ssl.NonValidatingFactory"
    }
}
