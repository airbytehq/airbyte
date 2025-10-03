/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.Connection
import java.util.function.Supplier

private val log = KotlinLogging.logger {}

/**
 * Factory for creating [java.sql.Connection], with possible SSH tunneling.
 *
 * The purpose of this object is to encapsulate and own an SSH tunnel session. If it exists, this
 * SSH tunnel session is shared by many connections.
 */
@Singleton
@Primary
class DatabricksSourceConnectionFactory(
    val config: JdbcSourceConfiguration,
) : Supplier<Connection> {

    val delegate = JdbcConnectionFactory(config)

    override fun get(): Connection {
        // Create connection directly without using delegate to avoid read-only mode
        val tunnelSession = delegate.ensureTunnelSession()
        val jdbcUrl: String =
            String.format(
                config.jdbcUrlFmt,
                tunnelSession.address.hostName,
                tunnelSession.address.port,
            )
        log.info { "Creating new connection for '$jdbcUrl'." }
        val props = java.util.Properties().apply { putAll(config.jdbcProperties) }
        // Databricks OSS JDBC does not support readOnly mode, so we don't set it
        return java.sql.DriverManager.getConnection(jdbcUrl, props)
    }
}
