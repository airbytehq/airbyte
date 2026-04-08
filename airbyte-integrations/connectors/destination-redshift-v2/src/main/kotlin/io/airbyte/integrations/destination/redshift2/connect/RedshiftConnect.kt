/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.connect

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.createTunnelSession
import io.airbyte.integrations.destination.redshift2.config.RedshiftConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlin.time.Duration.Companion.minutes
import kotlin.time.Duration.Companion.seconds
import org.apache.sshd.common.util.net.SshdSocketAddress

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
     * Resolves the database endpoint, tunneling through SSH if configured.
     *
     * When an SSH tunnel is configured, this opens a local port-forward to the remote
     * Redshift host and returns the tunnel's local address. When no tunnel is configured,
     * the direct host/port from the configuration is returned.
     */
    fun resolveEndpoint(): Pair<String, Int> {
        return when (val ssh = configuration.tunnelMethod) {
            is SshKeyAuthTunnelMethod,
            is SshPasswordAuthTunnelMethod -> {
                val remote = SshdSocketAddress(configuration.host, configuration.port)
                val sshConnectionOptions =
                    SshConnectionOptions.fromAdditionalProperties(emptyMap())
                val tunnel = createTunnelSession(remote, ssh, sshConnectionOptions)
                log.info {
                    "SSH tunnel established: ${configuration.host}:${configuration.port} " +
                        "-> ${tunnel.address.hostName}:${tunnel.address.port}"
                }
                tunnel.address.hostName to tunnel.address.port
            }
            is SshNoTunnelMethod,
            null -> configuration.host to configuration.port
        }
    }

    /**
     * Creates a fully configured [HikariDataSource] for Redshift.
     *
     * The DataSource is configured with:
     * - SSL enabled with non-validating factory (standard for Redshift)
     * - Redshift driver-level connect timeout of 120 seconds
     * - Connection keepalive at 30-second intervals
     * - Pool sizing: max 10, min idle 0 (connections created on demand)
     */
    fun createDataSource(): HikariDataSource {
        val (resolvedHost, resolvedPort) = resolveEndpoint()
        val jdbcUrl = buildJdbcUrl(resolvedHost, resolvedPort)

        log.info { "Creating Redshift DataSource for $resolvedHost:$resolvedPort/${configuration.database}" }

        val hikariConfig =
            HikariConfig().apply {
                connectionTimeout = 1.minutes.inWholeMilliseconds
                maximumPoolSize = 10
                minimumIdle = 0
                initializationFailTimeout = -1
                leakDetectionThreshold = 5.minutes.inWholeMilliseconds
                keepaliveTime = 30.seconds.inWholeMilliseconds
                driverClassName = DRIVER_CLASS
                this.jdbcUrl = jdbcUrl
                username = configuration.username
                password = configuration.password
                schema = configuration.schema

                addDataSourceProperty("ssl", "true")
                addDataSourceProperty("sslfactory", SSL_FACTORY)
                addDataSourceProperty("connectTimeout", 30.seconds.inWholeSeconds.toString())

                connectionTestQuery = "SELECT 1"
            }

        return HikariDataSource(hikariConfig)
    }

    private fun buildJdbcUrl(resolvedHost: String, resolvedPort: Int): String {
        val baseUrl = "jdbc:redshift://$resolvedHost:$resolvedPort/${configuration.database}"
        return if (configuration.jdbcUrlParams.isNullOrBlank()) {
            baseUrl
        } else {
            "$baseUrl?${configuration.jdbcUrlParams}"
        }
    }

    companion object {
        const val DRIVER_CLASS = "com.amazon.redshift.jdbc42.Driver"
        const val SSL_FACTORY = "com.amazon.redshift.ssl.NonValidatingFactory"
    }
}
