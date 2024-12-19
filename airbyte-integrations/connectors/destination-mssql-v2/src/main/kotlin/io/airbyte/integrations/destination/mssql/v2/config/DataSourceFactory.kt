/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.config

import com.microsoft.sqlserver.jdbc.SQLServerDataSource
import com.zaxxer.hikari.HikariDataSource
import io.micronaut.context.annotation.Factory
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
    val connectionStringArray =
        mutableListOf(
            "jdbc:sqlserver://${host}:${port}",
            "databaseName=${database}",
        )

    when (sslMethod) {
        is EncryptedVerify -> {
            connectionStringArray.add("encrypt=true")
            sslMethod.trustStoreName?.let { connectionStringArray.add("trustStoreName=$it") }
            sslMethod.trustStorePassword?.let {
                connectionStringArray.add("trustStorePassword=$it")
            }
            sslMethod.hostNameInCertificate?.let {
                connectionStringArray.add("hostNameInCertificate=$it")
            }
        }
        is EncryptedTrust -> {
            connectionStringArray.add("encrypt=true")
            connectionStringArray.add("trustServerCertificate=true")
        }
        is Unencrypted -> {}
    }

    jdbcUrlParams?.let { connectionStringArray.add(it) }

    return SQLServerDataSource().also {
        it.url = connectionStringArray.joinToString(";")
        it.user = user
        password?.let(it::setPassword)
    }
}
