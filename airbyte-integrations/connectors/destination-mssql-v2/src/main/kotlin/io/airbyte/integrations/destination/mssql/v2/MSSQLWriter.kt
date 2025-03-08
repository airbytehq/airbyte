/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationFailure
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.mssql.v2.config.AzureBlobStorageClientCreator
import io.airbyte.integrations.destination.mssql.v2.config.BulkLoadConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.InsertLoadTypeConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLDataSourceFactory
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import javax.sql.DataSource

@Singleton
class MSSQLWriter(
    private val config: MSSQLConfiguration,
    private val dataSourceFactory: MSSQLDataSourceFactory,
    @Value("\${airbyte.destination.core.record-batch-size-override:null}")
    private val recordBatchSizeOverride: Long? = null
) : DestinationWriter {

    /** Lazily initialized when [setup] is called. */
    private var dataSource: DataSource? = null

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        // Make sure dataSource is available
        val dataSourceNotNull =
            requireNotNull(dataSource) {
                "DataSource hasn't been initialized. Ensure 'setup()' was called."
            }

        // Build the SQL builder for this stream
        val sqlBuilder = MSSQLQueryBuilder(config.schema, stream)

        // Pick which loader to use based on the load type configuration
        return when (val loadConfig = config.mssqlLoadTypeConfiguration.loadTypeConfiguration) {
            is BulkLoadConfiguration -> {
                MSSQLBulkLoadStreamLoader(
                    stream = stream,
                    dataSource = dataSourceNotNull,
                    sqlBuilder = sqlBuilder,
                    bulkUploadDataSource = loadConfig.bulkLoadDataSource,
                    defaultSchema = config.schema,
                    azureBlobClient =
                        AzureBlobStorageClientCreator.createAzureBlobClient(loadConfig),
                    validateValuesPreLoad = loadConfig.validateValuesPreLoad ?: false,
                    recordBatchSizeOverride = recordBatchSizeOverride
                )
            }
            is InsertLoadTypeConfiguration -> {
                MSSQLStreamLoader(
                    dataSource = dataSourceNotNull,
                    stream = stream,
                    sqlBuilder = sqlBuilder
                )
            }
        }
    }

    /** Called once before loading begins. We initialize the DataSource here. */
    override suspend fun setup() {
        super.setup()
        dataSource = dataSourceFactory.getDataSource(config)
    }

    /** Called once after loading completes or fails. We dispose of the DataSource here. */
    override suspend fun teardown(destinationFailure: DestinationFailure?) {
        dataSource?.let { dataSourceFactory.disposeDataSource(it) }
        super.teardown(destinationFailure)
    }
}
