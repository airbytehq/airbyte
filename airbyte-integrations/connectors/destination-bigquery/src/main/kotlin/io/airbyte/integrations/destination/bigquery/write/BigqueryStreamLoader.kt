/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.bigquery.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.do_stuff_with_tables.BigqueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.do_stuff_with_tables.BigquerySqlGenerator
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.DestinationColumnNameMapping
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.TableNames

class BigqueryStreamLoader(
    override val stream: DestinationStream,
    config: BigqueryConfiguration,
    val tableNames: TableNames,
    val destinationHandler: BigqueryDestinationHandler,
    val sqlGenerator: BigquerySqlGenerator,
) : StreamLoader {
    private lateinit var destinationColumnNames: DestinationColumnNameMapping

    override suspend fun start() {
        super.start()
        // see AbstractStreamOperation.init
        // TODO also - CatalogParser's column name collision nonsense (populate
        // destinationColumnNames)

        // TODO do the truncate refresh garbage
        destinationHandler.execute(
            sqlGenerator.createRawTableIfNotExists(
                stream,
                tableNames.oldStyleRawTableName!!,
                suffix = ""
            )
        )
        destinationHandler.execute(
            sqlGenerator.createFinalTable(
                stream,
                tableNames.finalTableName!!,
                destinationColumnNames,
                suffix = "",
                force = false
            )
        )
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        super.close(streamFailure)
        // TODO execute T+D
        //   ... more truncate refresh nonsense
        // AbstractStreamOperation.finalizeTable
    }
}
