/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import com.microsoft.sqlserver.jdbc.SQLServerDataSource
import com.zaxxer.hikari.HikariDataSource
import io.micronaut.context.ApplicationContext
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import javax.sql.DataSource

@Factory
class DataSourceFactory {

    /**
     * Produces a pooled HikariDataSource for SQL Server, based on the given [MSSQLConfiguration].
     *
     * Note: This bean is managed by Micronaut’s IoC container. Whenever you inject or create a
     * [DataSource] in your code, Micronaut will provide an instance of this.
     */
    @Singleton
    fun dataSource(config: MSSQLConfiguration): DataSource {
        // Convert config to a “raw” SQLServerDataSource first
        val sqlServerDataSource = config.toSQLServerDataSource()

        // Wrap it with HikariCP for pooling
        return HikariDataSource().apply {
            dataSource = sqlServerDataSource
            connectionTimeout = 60_000
            connectionTestQuery = "SELECT 1"
            maximumPoolSize = 10
            minimumIdle = 0
            idleTimeout = 60_000
            leakDetectionThreshold = 0
        }
    }
}

/**
 * Converts an [MSSQLConfiguration] into a raw [SQLServerDataSource] by building the appropriate
 * JDBC URL and setting user credentials.
 */
fun MSSQLConfiguration.toSQLServerDataSource(): SQLServerDataSource {
    val connectionString = buildString {
        append("jdbc:sqlserver://$host:$port;databaseName=$database")

        // If we are using AD password-based auth, add the parameter
        if (authenticationMethod is ActiveDirectoryPassword) {
            append(";authentication=${authenticationMethod.name}")
        }

        // SSL settings
        when (sslMethod) {
            is EncryptedVerify -> {
                append(";encrypt=true")
                sslMethod.trustStoreName?.let { append(";trustStoreName=$it") }
                sslMethod.trustStorePassword?.let { append(";trustStorePassword=$it") }
                sslMethod.hostNameInCertificate?.let { append(";hostNameInCertificate=$it") }
            }
            is EncryptedTrust -> {
                append(";encrypt=true;trustServerCertificate=true")
            }
            is Unencrypted -> {
                append(";encrypt=false")
            }
        }

        // Additional arbitrary JDBC parameters
        jdbcUrlParams?.let { append(";$it") }
    }

    return SQLServerDataSource().also {
        it.url = connectionString
        it.user = user
        password?.let(it::setPassword)
    }
}

// Indirection to abstract the fact that we are leveraging micronaut to manage the datasource
// and avoid clients interacting directly with the application context to retrieve a datasource.
@Singleton
class MSSQLDataSourceFactory(private val applicationContext: ApplicationContext) {
    fun getDataSource(config: MSSQLConfiguration): DataSource =
        applicationContext.createBean(DataSource::class.java, config)

    fun disposeDataSource(dataSource: DataSource) {
        applicationContext.destroyBean(dataSource)
    }
}
