package io.airbyte.cdk.jdbc

import io.airbyte.cdk.command.ConnectorConfigurationSupplier
import io.airbyte.cdk.command.SourceConnectorConfiguration
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.ssh.createTunnelSession
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.net.InetSocketAddress
import java.sql.Connection
import java.sql.DriverManager
import java.util.*
import java.util.function.Supplier
import org.apache.sshd.common.util.net.SshdSocketAddress

private val logger = KotlinLogging.logger {}

/**
 * Factory for creating [java.sql.Connection], with possible SSH tunneling.
 */
@Singleton
class JdbcConnectionFactory(
    configSupplier: ConnectorConfigurationSupplier<SourceConnectorConfiguration>
) : Supplier<Connection>, AutoCloseable {

    val config: SourceConnectorConfiguration by lazy { configSupplier.get() }

    private val tunnelSessionDelegate: Lazy<TunnelSession> = lazy {
        val remote = SshdSocketAddress(config.realHost.trim(), config.realPort)
        createTunnelSession(remote, config.sshTunnel, config.sshConnectionOptions)
    }

    override fun close() {
        if (tunnelSessionDelegate.isInitialized()) {
            tunnelSessionDelegate.value.close()
        }
    }

    override fun get(): Connection {
        val address: InetSocketAddress = tunnelSessionDelegate.value.address
        val jdbcUrl: String = String.format(config.jdbcUrlFmt, address.hostName, address.port)
        logger.info { "Creating new connection for '$jdbcUrl'." }
        val props = Properties().apply { putAll(config.jdbcProperties) }
        return DriverManager.getConnection(jdbcUrl, props).also { it.isReadOnly = true }
    }
}
