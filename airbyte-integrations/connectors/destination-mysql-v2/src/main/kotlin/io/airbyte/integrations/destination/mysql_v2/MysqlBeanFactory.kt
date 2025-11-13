/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.check.CheckOperationV2
import io.airbyte.cdk.load.check.DestinationCheckerV2
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfiguration
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfigurationFactory
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlSpecification
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.util.logging.Logger
import javax.sql.DataSource

internal const val DATA_SOURCE_CONNECTION_TIMEOUT_MS = 30000L
internal const val DATA_SOURCE_IDLE_TIMEOUT_MS = 600000L
internal const val DATA_SOURCE_MAX_LIFETIME_MS = 1800000L

@Factory
class MysqlBeanFactory {

    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    fun mysqlConfiguration(
        configFactory: MysqlConfigurationFactory,
        specFactory: io.airbyte.cdk.command.ConfigurationSpecificationSupplier<MysqlSpecification>,
    ): MysqlConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
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
    fun emptyMysqlDataSource(): DataSource {
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
    fun mysqlDataSource(
        mysqlConfiguration: MysqlConfiguration,
        @Value("\${airbyte.edition:COMMUNITY}") airbyteEdition: String,
    ): HikariDataSource {
        // Build JDBC URL
        val baseUrl = "jdbc:mysql://${mysqlConfiguration.host}:${mysqlConfiguration.port}/${mysqlConfiguration.database}"

        // Add SSL mode if SSL is enabled
        val sslParam = if (mysqlConfiguration.ssl) {
            "sslMode=${mysqlConfiguration.sslMode.value}"
        } else {
            "sslMode=DISABLED"
        }

        // Combine with any additional JDBC parameters
        val jdbcUrl = if (mysqlConfiguration.jdbcUrlParams.isNullOrBlank()) {
            "$baseUrl?$sslParam"
        } else {
            "$baseUrl?$sslParam&${mysqlConfiguration.jdbcUrlParams}"
        }

        val datasourceConfig =
            HikariConfig().apply {
                connectionTimeout = DATA_SOURCE_CONNECTION_TIMEOUT_MS
                maximumPoolSize = 10 // Adjust based on workload
                minimumIdle = 0
                idleTimeout = DATA_SOURCE_IDLE_TIMEOUT_MS
                maxLifetime = DATA_SOURCE_MAX_LIFETIME_MS
                initializationFailTimeout = -1
                leakDetectionThreshold = DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L

                this.jdbcUrl = jdbcUrl
                username = mysqlConfiguration.username
                password = mysqlConfiguration.password
                driverClassName = "com.mysql.cj.jdbc.Driver"

                // MySQL-specific optimizations for batch operations
                // https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-configuration-properties.html

                // Enable server-side prepared statements for better performance
                addDataSourceProperty("useServerPrepStmts", "true")

                // Cache prepared statements
                addDataSourceProperty("cachePrepStmts", "true")
                addDataSourceProperty("prepStmtCacheSize", "250")
                addDataSourceProperty("prepStmtCacheSqlLimit", "2048")

                // Rewrite batched statements into multi-value INSERT for better performance
                addDataSourceProperty("rewriteBatchedStatements", "true")

                // Connection properties
                addDataSourceProperty("useUnicode", "true")
                addDataSourceProperty("characterEncoding", "UTF-8")

                // Enable compression for large data transfers
                addDataSourceProperty("useCompression", "true")

                // Socket timeout - prevents indefinite hanging
                addDataSourceProperty("socketTimeout", "60000")

                // Allow large packets for batch operations
                addDataSourceProperty("maxAllowedPacket", "67108864") // 64MB

                // Disable auto-commit for better batch performance
                addDataSourceProperty("autocommit", "false")

                // Set application name for identification
                addDataSourceProperty("connectionAttributes", "program_name:airbyte_${airbyteEdition.lowercase()}")
            }

        return HikariDataSource(datasourceConfig)
    }

    @Primary
    @Singleton
    @Requires(property = Operation.PROPERTY, value = "check")
    fun checkOperation(
        destinationChecker: DestinationCheckerV2,
        outputConsumer: OutputConsumer,
    ) = CheckOperationV2(destinationChecker, outputConsumer)

    @Singleton
    fun aggregatePublishingConfig(dataChannelMedium: DataChannelMedium): AggregatePublishingConfig {
        // Adjust based on whether we're in speed mode (gRPC) or normal mode (STDIO)
        return if (dataChannelMedium == DataChannelMedium.STDIO) {
            AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 250_000_000L, // 250MB per aggregate
                maxEstBytesAllAggregates = 250_000_000L * 5, // 1.25GB total
            )
        } else {
            // Speed mode - more aggressive buffering
            AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 250_000_000L,
                maxEstBytesAllAggregates = 250_000_000L * 5,
                maxBufferedAggregates = 6,
            )
        }
    }
}
