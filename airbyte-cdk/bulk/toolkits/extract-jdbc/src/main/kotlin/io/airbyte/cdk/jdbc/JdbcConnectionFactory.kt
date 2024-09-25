/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.ssh.createTunnelSession
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.DriverManager
import java.util.Properties
import java.util.concurrent.ConcurrentHashMap
import java.util.function.Supplier
import org.apache.sshd.common.util.net.SshdSocketAddress

private val log = KotlinLogging.logger {}

/**
 * Factory for creating [java.sql.Connection], with possible SSH tunneling.
 *
 * The purpose of this object is to encapsulate and own an SSH tunnel session. If it exists, this
 * SSH tunnel session is shared by many connections.
 */
@Singleton
class JdbcConnectionFactory(
    val config: JdbcSourceConfiguration,
) : Supplier<Connection> {

    fun ensureTunnelSession(): TunnelSession =
        tunnelSessions.computeIfAbsent(config) {
            val remote = SshdSocketAddress(it.realHost.trim(), it.realPort)
            createTunnelSession(remote, it.sshTunnel, it.sshConnectionOptions)
        }

    override fun get(): Connection {
        val tunnelSession: TunnelSession = ensureTunnelSession()
        val jdbcUrl: String =
            String.format(
                config.jdbcUrlFmt,
                tunnelSession.address.hostName,
                tunnelSession.address.port,
            )
        log.info { "Creating new connection for '$jdbcUrl'." }
        val props = Properties().apply { putAll(config.jdbcProperties) }
        return DriverManager.getConnection(jdbcUrl, props).also { it.isReadOnly = true }
    }

    companion object {
        /** This map exists to cater to tests which might not rely on dependency injection. */
        private val tunnelSessions = ConcurrentHashMap<SourceConfiguration, TunnelSession>()
    }
}
