/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.DestinationFailure
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import javax.inject.Singleton

@Singleton
class BigqueryWriter : DestinationWriter {
    override suspend fun setup() {
        TODO()
        // get bigquery client object
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return BigqueryStreamLoader(stream)
    }

    override suspend fun teardown(destinationFailure: DestinationFailure?) {
        TODO()
    }
}
