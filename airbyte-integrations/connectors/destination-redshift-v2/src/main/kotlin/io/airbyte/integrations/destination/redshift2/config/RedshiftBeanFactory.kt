/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.config

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.load.dataflow.config.model.AggregatePublishingConfig
import io.airbyte.cdk.load.table.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.redshift2.spec.RedshiftSpecification
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.util.logging.Logger
import javax.sql.DataSource

/**
 * Micronaut Factory for creating and wiring Redshift destination beans.
 */
@Factory
class RedshiftBeanFactory {

    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator =
        DefaultTempTableNameGenerator(internalNamespace = null)

    @Singleton
    fun redshiftConfiguration(
        configFactory: RedshiftConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<RedshiftSpecification>
    ): RedshiftConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    /**
     * Dummy DataSource for the spec operation.
     * The spec operation doesn't have a configuration, so we can't create a real database connection.
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

    /**
     * Creates the HikariCP DataSource for Redshift connections.
     */
    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun redshiftDataSource(redshiftConfiguration: RedshiftConfiguration): HikariDataSource {
        val datasourceConfig =
            HikariConfig().apply {
                connectionTimeout = 60_000L
                maximumPoolSize = 10
                minimumIdle = 0
                initializationFailTimeout = -1
                leakDetectionThreshold = 300_000L
                driverClassName = "com.amazon.redshift.jdbc42.Driver"
                jdbcUrl = redshiftConfiguration.jdbcUrl
                username = redshiftConfiguration.username
                password = redshiftConfiguration.password
                schema = redshiftConfiguration.schema

                // Apply custom JDBC URL parameters if provided
                redshiftConfiguration.jdbcUrlParams?.let { params ->
                    JdbcUtils.parseJdbcParameters(params).forEach { (key, value) ->
                        addDataSourceProperty(key, value)
                    }
                }

                // Configure connection validation
                connectionTestQuery = "SELECT 1"
            }

        return HikariDataSource(datasourceConfig)
    }

    /**
     * Configures batch sizes for aggregating records before writing.
     * For Redshift, we use larger batch sizes for optimal S3 COPY performance.
     */
    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig {
        return AggregatePublishingConfig(
            maxRecordsPerAgg = 50_000
        )
    }
}
