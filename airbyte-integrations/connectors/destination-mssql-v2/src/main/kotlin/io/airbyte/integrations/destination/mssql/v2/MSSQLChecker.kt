/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLDataSourceFactory
import jakarta.inject.Singleton
import java.util.UUID
import javax.sql.DataSource

@Singleton
class MSSQLChecker(private val dataSourceFactory: MSSQLDataSourceFactory) :
    DestinationChecker<MSSQLConfiguration> {
    private val testStream =
        DestinationStream(
            descriptor =
                DestinationStream.Descriptor(
                    namespace = null,
                    name = "check_test_${UUID.randomUUID()}",
                ),
            importType = Append,
            schema = ObjectType(linkedMapOf("id" to FieldType(IntegerType, nullable = true))),
            generationId = 0L,
            minimumGenerationId = 0L,
            syncId = 0L,
        )

    override fun check(config: MSSQLConfiguration) {
        val dataSource: DataSource = dataSourceFactory.getDataSource(config)
        val sqlBuilder = MSSQLQueryBuilder(config, testStream)

        dataSource.connection.use { connection ->
            sqlBuilder.createTableIfNotExists(connection)
            sqlBuilder.dropTable(connection)
        }
    }
}
