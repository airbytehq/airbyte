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
        val jdbcUrl = "jdbc:redshift://$endpoint/${configuration.database}"
        val connectionProperties = buildConnectionProperties()

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

                connectionProperties.forEach { (key, value) -> addDataSourceProperty(key, value) }
            }

        return HikariDataSource(hikariConfig)
    }

    /** Merges default SSL connection properties with user-provided jdbc_url_params */
    internal fun buildConnectionProperties(): Map<String, String> {
        val userParams = parseJdbcUrlParams(configuration.jdbcUrlParams)

        val properties =
            mutableMapOf(
                "ssl" to "true",
                "sslfactory" to SSL_FACTORY,
            )

        // sslmode and sslfactory are mutually exclusive in the Redshift JDBC driver.
        if (userParams.containsKey("sslmode")) {
            properties.remove("sslfactory")
        }

        // User params override remaining defaults
        properties.putAll(userParams)
        return properties
    }

    companion object {
        const val SSL_FACTORY = "com.amazon.redshift.ssl.NonValidatingFactory"

        /**
         * Parses a jdbc_url_params string (e.g. "key1=value1&key2=value2") into a Map. Returns an
         * empty map for null or blank input.
         */
        internal fun parseJdbcUrlParams(params: String?): Map<String, String> {
            if (params.isNullOrBlank()) return emptyMap()
            return params
                .split("&")
                .filter { it.contains("=") }
                .associate { param ->
                    val (key, value) = param.split("=", limit = 2)
                    key.trim() to value.trim()
                }
        }
    }
}
