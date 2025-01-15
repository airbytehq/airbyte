/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationFailure
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLDataSourceFactory
import jakarta.inject.Singleton
import javax.sql.DataSource

@Singleton
class MSSQLWriter(
    private val config: MSSQLConfiguration,
    private val dataSourceFactory: MSSQLDataSourceFactory
) : DestinationWriter {
    private var dataSource: DataSource? = null

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val sqlBuilder = MSSQLQueryBuilder(config, stream)
        return MSSQLStreamLoader(
            dataSource = dataSource ?: throw IllegalStateException("dataSource hasn't been initialized"),
            stream = stream,
            sqlBuilder = sqlBuilder,
        )
    }

    override suspend fun setup() {
        super.setup()
        dataSource = dataSourceFactory.getDataSource(config)
    }

    override suspend fun teardown(destinationFailure: DestinationFailure?) {
        dataSource?.let { dataSourceFactory.disposeDataSource(it) }
        super.teardown(destinationFailure)
    }

}
