/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.config

import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.Operation
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
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
    fun redshiftConfiguration(
        configFactory: RedshiftConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<RedshiftSpecification>
    ): RedshiftConfiguration {
        val spec = specFactory.get()
        return configFactory.makeWithoutExceptionHandling(spec)
    }

    /**
     * Dummy DataSource for the spec operation.
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
     * Creates the HikariCP DataSource for Redshift connections,
     * delegating to [RedshiftConnect] for connection configuration,
     * SSH tunnel resolution, and SSL setup.
     */
    @Singleton
    @Requires(property = Operation.PROPERTY, notEquals = "spec")
    fun redshiftDataSource(redshiftConnect: RedshiftConnect): HikariDataSource {
        return redshiftConnect.createDataSource()
    }
}
