/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.motherduck

import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckConfiguration
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckConfigurationFactory
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckSpecification
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.util.logging.Logger
import javax.sql.DataSource

@Factory
class MotherDuckBeansFactory {

    @Singleton
    fun tempTableNameGenerator(
        motherDuckConfig: MotherDuckConfiguration,
    ): TempTableNameGenerator =
        DefaultTempTableNameGenerator(internalNamespace = motherDuckConfig.internalTableSchema)

    @Singleton
    fun motherDuckConfiguration(
        configFactory: MotherDuckConfigurationFactory,
        spec: MotherDuckSpecification,
    ): MotherDuckConfiguration {
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    @Requires(property = Operation.PROPERTY, value = "spec")
    fun emptyMotherDuckDataSource(): DataSource {
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
    fun motherDuckDataSource(
        motherDuckConfiguration: MotherDuckConfiguration,
    ): HikariDataSource {
        val jdbcUrl = buildString {
            append("jdbc:duckdb:")
            append(motherDuckConfiguration.destinationPath)

            if (motherDuckConfiguration.destinationPath.startsWith("md:")) {
                append("?motherduck_token=")
                append(motherDuckConfiguration.motherduckApiKey)
            }
        }

        val datasourceConfig =
            HikariConfig().apply {
                connectionTimeout = 30000L
                maximumPoolSize = 10
                minimumIdle = 0
                idleTimeout = 600000L
                initializationFailTimeout = -1
                leakDetectionThreshold = 40000L
                maxLifetime = 610000L
                driverClassName = "org.duckdb.DuckDBDriver"
                this.jdbcUrl = jdbcUrl

                addDataSourceProperty("access_mode", "READ_WRITE")

                schema = motherDuckConfiguration.schema
            }

        return HikariDataSource(datasourceConfig)
    }
}
