/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.ssh.createTunnelSession
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2ConfigurationFactory
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Specification
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.util.logging.Logger
import javax.sql.DataSource
import org.apache.sshd.common.util.net.SshdSocketAddress

private val log = KotlinLogging.logger {}

internal const val DATA_SOURCE_CONNECTION_TIMEOUT_MS = 30000L
internal const val DATA_SOURCE_IDLE_TIMEOUT_MS = 600000L
internal const val DATA_SOURCE_MAX_POOL_SIZE = 10

@Factory
class RedshiftV2BeanFactory {

    @Singleton
    fun tempTableNameGenerator(
        config: RedshiftV2Configuration,
    ): TempTableNameGenerator =
        DefaultTempTableNameGenerator(internalNamespace = config.internalSchema)

    @Singleton
    fun redshiftConfiguration(
        configFactory: RedshiftV2ConfigurationFactory,
        specSupplier:
            io.airbyte.cdk.command.ConfigurationSpecificationSupplier<RedshiftV2Specification>,
    ): RedshiftV2Configuration {
        val spec = specSupplier.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    /**
     * Creates the SSH tunnel session if configured. The tunnel session manages the SSH connection
     * lifecycle.
     */
    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun tunnelSession(
        config: RedshiftV2Configuration,
    ): TunnelSession {
        log.info { "Creating tunnel session for ${config.realHost}:${config.realPort}" }
        val remote = SshdSocketAddress(config.realHost, config.realPort)
        val session = createTunnelSession(remote, config.sshTunnel, config.sshConnectionOptions)

        // Update config with tunneled host/port
        config.tunnelHost = session.address.hostString
        config.tunnelPort = session.address.port
        log.info {
            "Tunnel session created, connecting via ${config.tunnelHost}:${config.tunnelPort}"
        }

        return session
    }

    /**
     * Dummy DataSource for the spec operation. Spec doesn't have a configuration present, so we
     * cannot create the real data source.
     */
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "spec")
    fun emptyRedshiftDataSource(): DataSource {
        return object : DataSource {
            override fun getConnection(): Connection? = null
            override fun getConnection(username: String, password: String): Connection? =
                getConnection()
            override fun getLogWriter(): PrintWriter =
                PrintWriter(System.out.writer(StandardCharsets.UTF_8))
            override fun setLogWriter(out: PrintWriter) {}
            override fun setLoginTimeout(seconds: Int) {}
            override fun getLoginTimeout(): Int = 0
            override fun getParentLogger(): Logger = Logger.getGlobal()
            override fun <T : Any> unwrap(iface: Class<T>): T? = null
            override fun isWrapperFor(iface: Class<*>): Boolean = false
        }
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun redshiftDataSource(
        config: RedshiftV2Configuration,
        @Suppress("UNUSED_PARAMETER")
        tunnelSession: TunnelSession, // Ensure tunnel is created first
    ): HikariDataSource {
        log.info { "Creating Redshift DataSource with JDBC URL: ${config.jdbcUrl}" }

        val datasourceConfig =
            HikariConfig().apply {
                connectionTimeout = DATA_SOURCE_CONNECTION_TIMEOUT_MS
                maximumPoolSize = DATA_SOURCE_MAX_POOL_SIZE
                minimumIdle = 0
                idleTimeout = DATA_SOURCE_IDLE_TIMEOUT_MS
                initializationFailTimeout = -1
                leakDetectionThreshold = DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L
                maxLifetime = DATA_SOURCE_IDLE_TIMEOUT_MS + 10000L
                driverClassName = "com.amazon.redshift.jdbc42.Driver"
                jdbcUrl = config.jdbcUrl
                username = config.username
                password = config.password
            }

        return HikariDataSource(datasourceConfig)
    }

    @Singleton
    fun aggregatePublishingConfig(dataChannelMedium: DataChannelMedium): AggregatePublishingConfig {
        // Target ~50MB per aggregate for optimal Redshift COPY performance
        val maxBytesPerAgg = 50_000_000L
        return if (dataChannelMedium == DataChannelMedium.STDIO) {
            AggregatePublishingConfig(
                maxRecordsPerAgg = 100_000L,
                maxEstBytesPerAgg = maxBytesPerAgg,
                maxEstBytesAllAggregates = maxBytesPerAgg * 5,
            )
        } else {
            AggregatePublishingConfig(
                maxRecordsPerAgg = 100_000L,
                maxEstBytesPerAgg = maxBytesPerAgg,
                maxEstBytesAllAggregates = maxBytesPerAgg * 5,
                maxBufferedAggregates = 6,
            )
        }
    }
}
