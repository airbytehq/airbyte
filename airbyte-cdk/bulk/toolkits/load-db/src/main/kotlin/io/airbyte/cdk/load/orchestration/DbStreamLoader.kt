package io.airbyte.cdk.load.orchestration

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader

class DbStreamLoader(override val stream: DestinationStream) : StreamLoader {
    override suspend fun start() {
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
    }
}
