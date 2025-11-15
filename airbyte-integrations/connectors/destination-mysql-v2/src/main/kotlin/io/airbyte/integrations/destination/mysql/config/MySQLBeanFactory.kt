package io.airbyte.integrations.destination.mysql.config

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import io.airbyte.integrations.destination.mysql.spec.MySQLConfigurationFactory
import io.airbyte.integrations.destination.mysql.spec.MySQLSpecification
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.util.logging.Logger
import javax.sql.DataSource

internal const val DATA_SOURCE_CONNECTION_TIMEOUT_MS = 30000L
internal const val DATA_SOURCE_IDLE_TIMEOUT_MS = 600000L

@Factory
class MySQLBeanFactory {

    @Singleton
    fun mysqlConfiguration(
        configFactory: MySQLConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<MySQLSpecification>,
    ): MySQLConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()

    @Singleton
    fun initialStatusGatherer(
        client: io.airbyte.cdk.load.component.TableOperationsClient,
        tempTableNameGenerator: TempTableNameGenerator,
    ): io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer<io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus> {
        return MySQLDirectLoadDatabaseInitialStatusGatherer(client, tempTableNameGenerator)
    }

    @Singleton
    fun aggregatePublishingConfig(dataChannelMedium: io.airbyte.cdk.load.config.DataChannelMedium): io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig {
        // Different settings for STDIO vs SOCKET mode
        return if (dataChannelMedium == io.airbyte.cdk.load.config.DataChannelMedium.STDIO) {
            io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 350_000_000L,
                maxEstBytesAllAggregates = 350_000_000L * 5,
            )
        } else {
            // SOCKET mode (faster IPC)
            io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 350_000_000L,
                maxEstBytesAllAggregates = 350_000_000L * 5,
                maxBufferedAggregates = 6,
            )
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
    fun emptyMySQLDataSource(): DataSource {
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
        mysqlConfiguration: MySQLConfiguration,
    ): HikariDataSource {
        val mysqlJdbcUrl =
            "jdbc:mysql://${mysqlConfiguration.hostname}:${mysqlConfiguration.port}/${mysqlConfiguration.database}"

        val datasourceConfig =
            HikariConfig().apply {
                connectionTimeout = DATA_SOURCE_CONNECTION_TIMEOUT_MS
                maximumPoolSize = 10
                minimumIdle = 0
                idleTimeout = DATA_SOURCE_IDLE_TIMEOUT_MS
                initializationFailTimeout = -1
                leakDetectionThreshold = DATA_SOURCE_CONNECTION_TIMEOUT_MS + 10000L
                maxLifetime = DATA_SOURCE_IDLE_TIMEOUT_MS + 10000L
                driverClassName = "com.mysql.cj.jdbc.Driver"
                jdbcUrl = mysqlJdbcUrl
                username = mysqlConfiguration.username
                password = mysqlConfiguration.password

                // MySQL specific configurations
                // Use server-side prepared statements for better performance
                addDataSourceProperty("cachePrepStmts", "true")
                addDataSourceProperty("prepStmtCacheSize", "250")
                addDataSourceProperty("prepStmtCacheSqlLimit", "2048")
                // Use newer JDBC protocol
                addDataSourceProperty("useServerPrepStmts", "true")
                // Enable compression for large data transfers
                addDataSourceProperty("useCompression", "true")
                // Set timezone to UTC for consistency
                addDataSourceProperty("serverTimezone", "UTC")
                // Disable SSL by default (can be configured later if needed)
                addDataSourceProperty("useSSL", "false")
                addDataSourceProperty("allowPublicKeyRetrieval", "true")
            }

        return HikariDataSource(datasourceConfig)
    }
}
