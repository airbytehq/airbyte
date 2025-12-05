/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.config

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.util.PostgresSslConnectionUtils
import io.airbyte.cdk.load.check.CheckOperationV2
import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.createTunnelSession
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.spec.PostgresConfigurationFactory
import io.airbyte.integrations.destination.postgres.spec.PostgresSpecification
import io.airbyte.integrations.destination.postgres.spec.SslModeVerifyCa
import io.airbyte.integrations.destination.postgres.spec.SslModeVerifyFull
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.util.logging.Logger
import javax.sql.DataSource
import org.apache.sshd.common.util.net.SshdSocketAddress

internal const val DATA_SOURCE_CONNECTION_TIMEOUT_MS = 30000L
internal const val DATA_SOURCE_IDLE_TIMEOUT_MS = 600000L

@Factory
class PostgresBeanFactory {

    @Singleton
    fun tempTableNameGenerator(
        postgresConfig: PostgresConfiguration,
    ): TempTableNameGenerator =
        DefaultTempTableNameGenerator(internalNamespace = postgresConfig.internalTableSchema)

    @Singleton
    fun postgresConfiguration(
        configFactory: PostgresConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<PostgresSpecification>,
    ): PostgresConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    /** Helper to resolve the endpoint (either direct or through SSH tunnel) */
    @Singleton
    @Named("resolvedHost")
    fun resolvedHost(config: PostgresConfiguration): String {
        return when (val ssh = config.tunnelMethod) {
            is SshKeyAuthTunnelMethod,
            is SshPasswordAuthTunnelMethod -> {
                val remote = SshdSocketAddress(config.host, config.port)
                val sshConnectionOptions: SshConnectionOptions =
                    SshConnectionOptions.fromAdditionalProperties(emptyMap())
                val tunnel = createTunnelSession(remote, ssh, sshConnectionOptions)
                tunnel.address.hostName
            }
            is SshNoTunnelMethod,
            null -> config.host
        }
    }

    @Singleton
    @Named("resolvedPort")
    fun resolvedPort(config: PostgresConfiguration): Int {
        return when (val ssh = config.tunnelMethod) {
            is SshKeyAuthTunnelMethod,
            is SshPasswordAuthTunnelMethod -> {
                val remote = SshdSocketAddress(config.host, config.port)
                val sshConnectionOptions: SshConnectionOptions =
                    SshConnectionOptions.fromAdditionalProperties(emptyMap())
                val tunnel = createTunnelSession(remote, ssh, sshConnectionOptions)
                tunnel.address.port
            }
            is SshNoTunnelMethod,
            null -> config.port
        }
    }

    /**
     * Dummy [DataSource] for the spec operation. Spec doesn't have a configuration present, so we
     * cannot create the real data source. However, to avoid having to pull conditional checks on
     * every singleton related to using the data source, we can simply create a dummy one here so
     * that everything will be wired correctly even if all of those beans are unused when running
     * the spec operation.
     */
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "spec")
    fun emptyPostgresDataSource(): DataSource {
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
    fun postgresDataSource(
        postgresConfiguration: PostgresConfiguration,
        @Named("resolvedHost") resolvedHost: String,
        @Named("resolvedPort") resolvedPort: Int,
    ): HikariDataSource {
        val postgresJdbcUrl =
            "jdbc:postgresql://$resolvedHost:$resolvedPort/${postgresConfiguration.database}"

        val datasourceConfig =
            HikariConfig().apply {
                connectionTimeout = DATA_SOURCE_CONNECTION_TIMEOUT_MS
                maximumPoolSize = 10
                minimumIdle = 0
                idleTimeout = DATA_SOURCE_IDLE_TIMEOUT_MS
                initializationFailTimeout = -1
                leakDetectionThreshold = DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L
                maxLifetime = DATA_SOURCE_IDLE_TIMEOUT_MS + 10000L
                driverClassName = "org.postgresql.Driver"
                jdbcUrl = postgresJdbcUrl
                username = postgresConfiguration.username
                password = postgresConfiguration.password ?: ""
                schema = postgresConfiguration.schema

                // Apply custom JDBC URL parameters first (if provided)
                postgresConfiguration.jdbcUrlParams?.let { params ->
                    JdbcUtils.parseJdbcParameters(params).forEach { (key, value) ->
                        addDataSourceProperty(key, value)
                    }
                }

                // Apply SSL connection parameters as data source properties
                // These are applied AFTER custom params to ensure SSL config takes precedence
                if (postgresConfiguration.ssl) {
                    val sslConnectionParams =
                        buildSslConnectionParams(postgresConfiguration.sslMode)
                    sslConnectionParams.forEach { (key, value) ->
                        addDataSourceProperty(key, value)
                    }
                }
            }

        return HikariDataSource(datasourceConfig)
    }

    private fun buildSslConnectionParams(
        sslMode: io.airbyte.integrations.destination.postgres.spec.SslMode?
    ): Map<String, String> {
        return when (sslMode) {
            is SslModeVerifyCa -> {
                val sslModeJson =
                    Jsons.jsonNode(
                        mapOf(
                            PostgresSslConnectionUtils.PARAM_MODE to
                                PostgresSslConnectionUtils.VERIFY_CA,
                            PostgresSslConnectionUtils.PARAM_CA_CERTIFICATE to
                                sslMode.caCertificate,
                            PostgresSslConnectionUtils.PARAM_CLIENT_KEY_PASSWORD to
                                (sslMode.clientKeyPassword ?: "")
                        )
                    )
                PostgresSslConnectionUtils.obtainConnectionOptions(sslModeJson)
            }
            is SslModeVerifyFull -> {
                val sslModeJson =
                    Jsons.jsonNode(
                        mapOf(
                            PostgresSslConnectionUtils.PARAM_MODE to
                                PostgresSslConnectionUtils.VERIFY_FULL,
                            PostgresSslConnectionUtils.PARAM_CA_CERTIFICATE to
                                sslMode.caCertificate,
                            PostgresSslConnectionUtils.PARAM_CLIENT_CERTIFICATE to
                                sslMode.clientCertificate,
                            PostgresSslConnectionUtils.PARAM_CLIENT_KEY to sslMode.clientKey,
                            PostgresSslConnectionUtils.PARAM_CLIENT_KEY_PASSWORD to
                                (sslMode.clientKeyPassword ?: "")
                        )
                    )
                PostgresSslConnectionUtils.obtainConnectionOptions(sslModeJson)
            }
            null -> emptyMap()
            else -> {
                // For other SSL modes (disable, allow, prefer, require), return the mode parameter
                mapOf(
                    PostgresSslConnectionUtils.PARAM_SSL to
                        PostgresSslConnectionUtils.TRUE_STRING_VALUE,
                    PostgresSslConnectionUtils.PARAM_SSLMODE to sslMode.mode
                )
            }
        }
    }

    @Primary
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "check")
    fun checkOperation(
        destinationChecker: DestinationCheckerV2,
        outputConsumer: OutputConsumer,
    ) = CheckOperationV2(destinationChecker, outputConsumer)

    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig {
        return AggregatePublishingConfig()
    }
}
