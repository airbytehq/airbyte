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
    fun dataSource(): DataSource { // configuration: MSSQLConfiguration): DataSource {
        val sqlServerDataSource = SQLServerDataSource()
        sqlServerDataSource.url =
            "jdbc:sqlserver://localhost:1433;encrypt=true;trustServerCertificate=true;databaseName=test;applicationName=destination-mssql-v2"
        sqlServerDataSource.user = "sa"
        sqlServerDataSource.setPassword("Averycomplicatedpassword1!")
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
