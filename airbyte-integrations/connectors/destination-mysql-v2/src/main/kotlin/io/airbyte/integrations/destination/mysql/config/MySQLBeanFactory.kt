/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.config

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshKeyAuthTunnelMethod
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.createTunnelSession
import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import io.airbyte.integrations.destination.mysql.spec.MySQLConfigurationFactory
import io.airbyte.integrations.destination.mysql.spec.MySQLSpecification
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton
import org.apache.sshd.common.util.net.SshdSocketAddress
import javax.sql.DataSource

private val logger = KotlinLogging.logger {}

@Factory
class MySQLBeanFactory {

    @Singleton
    fun configuration(
        configFactory: MySQLConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<MySQLSpecification>,
    ): MySQLConfiguration {
        val spec = specFactory.get()
        logger.info { "MySQLSpecification parsed: hostname='${spec.hostname}', port=${spec.port}, database='${spec.database}', username='${spec.username}', sslMode=${spec.sslMode}" }
        logger.info { "MySQLSpecification class: ${spec::class.java.name}" }
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    @Named("resolvedHost")
    fun resolvedHost(config: MySQLConfiguration): String {
        return when (val ssh = config.tunnelConfig) {
            is SshKeyAuthTunnelMethod,
            is SshPasswordAuthTunnelMethod -> {
                val remote = SshdSocketAddress(config.hostname, config.port)
                val sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap())
                val tunnel = createTunnelSession(remote, ssh, sshConnectionOptions)
                tunnel.address.hostName
            }
            is SshNoTunnelMethod,
            null -> config.hostname
        }
    }

    @Singleton
    @Named("resolvedPort")
    fun resolvedPort(config: MySQLConfiguration): Int {
        return when (val ssh = config.tunnelConfig) {
            is SshKeyAuthTunnelMethod,
            is SshPasswordAuthTunnelMethod -> {
                val remote = SshdSocketAddress(config.hostname, config.port)
                val sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap())
                val tunnel = createTunnelSession(remote, ssh, sshConnectionOptions)
                tunnel.address.port
            }
            is SshNoTunnelMethod,
            null -> config.port
        }
    }

    @Singleton
    fun dataSource(
        config: MySQLConfiguration,
        @Named("resolvedHost") host: String,
        @Named("resolvedPort") port: Int,
    ): DataSource {
        val jdbcUrl = buildJdbcUrl(host, port, config)
        logger.info { "Creating MySQL DataSource with config: host=$host, port=$port, database=${config.database}, username=${config.username}, sslMode=${config.sslMode}, jdbcUrl=$jdbcUrl" }
        val hikariConfig = HikariConfig().apply {
            this.jdbcUrl = jdbcUrl
            username = config.username
            password = config.password
            maximumPoolSize = 2
            minimumIdle = 0
            connectionTimeout = 30000
            idleTimeout = 60000
            maxLifetime = 30000
            driverClassName = "com.mysql.cj.jdbc.Driver"
        }
        return HikariDataSource(hikariConfig)
    }

    private fun buildJdbcUrl(host: String, port: Int, config: MySQLConfiguration): String {
        val params = mutableListOf<String>()

        // SSL mode mapping
        when (config.sslMode) {
            "disabled" -> params.add("sslMode=DISABLED")
            "preferred" -> params.add("sslMode=PREFERRED")
            "required" -> params.add("sslMode=REQUIRED")
            "verify_ca" -> params.add("sslMode=VERIFY_CA")
            "verify_identity" -> params.add("sslMode=VERIFY_IDENTITY")
        }

        // Additional recommended parameters
        params.add("useUnicode=true")
        params.add("characterEncoding=UTF-8")
        params.add("zeroDateTimeBehavior=CONVERT_TO_NULL")
        params.add("allowPublicKeyRetrieval=true")

        val paramString = if (params.isNotEmpty()) "?${params.joinToString("&")}" else ""
        // Don't specify database in URL - we create databases dynamically
        return "jdbc:mysql://$host:$port$paramString"
    }

    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig = AggregatePublishingConfig()
}
