/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import com.microsoft.sqlserver.jdbc.SQLServerDataSource
import com.zaxxer.hikari.HikariDataSource
import jakarta.inject.Singleton
import javax.sql.DataSource

@Factory
class DataSourceFactory {

    @Singleton
    fun dataSource(config: MSSQLConfiguration): DataSource {
        val sqlServerDataSource = config.toSQLServerDataSource()
        val dataSource = HikariDataSource()
        dataSource.dataSource = sqlServerDataSource
        dataSource.connectionTimeout = 30000
        dataSource.connectionTestQuery = "SELECT 1"
        dataSource.maximumPoolSize = 10
        dataSource.minimumIdle = 0
        dataSource.idleTimeout = 60000
        dataSource.leakDetectionThreshold = dataSource.connectionTimeout + 10000
        return dataSource
    }
}

fun MSSQLConfiguration.toSQLServerDataSource(): SQLServerDataSource {
    val connectionString = StringBuilder().apply {
        append("jdbc:sqlserver://${host}:${port};databaseName=${database}")

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
            is Unencrypted -> {}
        }

        jdbcUrlParams?.let { append(";$it") }
    }.toString()

    return SQLServerDataSource().also {
        it.url = connectionString
        it.user = user
        password?.let(it::setPassword)
    }
}
