/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationFailure
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.bigquery.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.probably_core_stuff.TableNames
import javax.inject.Singleton

@Singleton
class BigqueryWriter(val config: BigqueryConfiguration) : DestinationWriter {
    private lateinit var tableNames: Map<DestinationStream.Descriptor, TableNames>

    override suspend fun setup() {
        TODO()
        // get bigquery client object
        // do CatalogParser's table name collision nonsense - have some logic to build
        // Map<DestinationStream.Descriptor, TableNames> or something?
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return BigqueryStreamLoader(stream, config, tableNames[stream.descriptor])
    }

    override suspend fun teardown(destinationFailure: DestinationFailure?) {
        TODO()
    }
}
