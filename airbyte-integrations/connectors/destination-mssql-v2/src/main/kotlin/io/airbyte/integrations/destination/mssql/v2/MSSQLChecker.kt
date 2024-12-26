package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLDataSourceFactory
import jakarta.inject.Singleton
import java.util.UUID
import javax.sql.DataSource

@Singleton
class MSSQLChecker(private val dataSourceFactory: MSSQLDataSourceFactory) : DestinationChecker<MSSQLConfiguration> {
    override fun check(config: MSSQLConfiguration) {
        val dataSource: DataSource = dataSourceFactory.getDataSource(config)
        val testTableName = "check_test_${UUID.randomUUID()}"
        val fullyQualifiedTableName = "[${config.rawDataSchema}].[${testTableName}]"
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.executeUpdate(
                    """
                    CREATE TABLE ${fullyQualifiedTableName} (test int);
                    DROP TABLE ${fullyQualifiedTableName};
                    """.trimIndent(),
                )
            }
        }
    }
}
