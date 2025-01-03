/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLDataSourceFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import javax.sql.DataSource

@Singleton
class MSSQLWriter(
    private val config: MSSQLConfiguration,
    private val dataSourceFactory: MSSQLDataSourceFactory
) : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val dataSource = dataSourceFactory.getDataSource(config)
        val sqlBuilder = MSSQLQueryBuilder(config, stream)
        ensureTableExists(dataSource, sqlBuilder)
        return MSSQLStreamLoader(dataSource = dataSource, stream = stream, sqlBuilder = sqlBuilder)
    }

    private fun ensureTableExists(dataSource: DataSource, sqlBuilder: MSSQLQueryBuilder) {
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    statement.executeUpdate(sqlBuilder.createFinalSchemaIfNotExists())
                }
                connection.createStatement().use { statement ->
                    statement.executeUpdate(sqlBuilder.createFinalTableIfNotExists())
                }
            }
        } catch (ex: Exception) {
            KotlinLogging.logger {}.error(ex) { ex.message }
            throw ex
        }
    }
}
