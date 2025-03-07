/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.bigquery.BigqueryConfiguration

class BigqueryStreamLoader(override val stream: DestinationStream, config: BigqueryConfiguration) :
    StreamLoader {
    override suspend fun start() {
        super.start()
        // TODO create raw+final table if not exists
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        super.close(streamFailure)
        // TODO execute T+D
    }
}
