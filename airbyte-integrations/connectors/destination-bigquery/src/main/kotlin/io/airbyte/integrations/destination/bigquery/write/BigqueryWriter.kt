/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationFailure
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.bigquery.BigqueryConfiguration
import javax.inject.Singleton

@Singleton
class BigqueryWriter(val config: BigqueryConfiguration) : DestinationWriter {
    override suspend fun setup() {
        TODO()
        // get bigquery client object
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return BigqueryStreamLoader(stream, config)
    }

    override suspend fun teardown(destinationFailure: DestinationFailure?) {
        TODO()
    }
}
