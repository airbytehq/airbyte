/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLDataSourceFactory
import jakarta.inject.Singleton
import java.util.UUID
import javax.sql.DataSource

const val CHECK_TABLE_STATEMENT = """
    CREATE TABLE ? (test int);
    DROP TABLE ?;
"""

@Singleton
class MSSQLChecker(private val dataSourceFactory: MSSQLDataSourceFactory) :
    DestinationChecker<MSSQLConfiguration> {
    override fun check(config: MSSQLConfiguration) {
        val dataSource: DataSource = dataSourceFactory.getDataSource(config)
        val testTableName = "check_test_${UUID.randomUUID()}"
        val fullyQualifiedTableName = "[${config.rawDataSchema}].[${testTableName}]"
        dataSource.connection.use { connection ->
            connection.prepareStatement(CHECK_TABLE_STATEMENT.trimIndent()).use { statement ->
                statement.setString(1, fullyQualifiedTableName)
                statement.setString(2, fullyQualifiedTableName)
                statement.executeUpdate()
            }
        }
    }
}
