package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.mssql.v2.config.DataSourceFactory
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import jakarta.inject.Singleton

@Singleton
class MSSQLChecker(private val dataSourceFactory: DataSourceFactory) : DestinationChecker<MSSQLConfiguration> {
    override fun check(config: MSSQLConfiguration) {
        val dataSource = dataSourceFactory.dataSource(config)
        dataSource.connection.use { }
    }
}
