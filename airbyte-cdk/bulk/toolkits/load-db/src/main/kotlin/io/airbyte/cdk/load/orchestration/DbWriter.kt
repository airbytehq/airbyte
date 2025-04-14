package io.airbyte.cdk.load.orchestration

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader

class DbWriter : DestinationWriter {
    override suspend fun setup() {
        // create all namespaces
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        TODO("Not yet implemented")
    }
}
