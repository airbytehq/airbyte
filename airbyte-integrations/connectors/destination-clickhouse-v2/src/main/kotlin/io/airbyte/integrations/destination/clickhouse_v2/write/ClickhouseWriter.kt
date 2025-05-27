package io.airbyte.integrations.destination.clickhouse_v2.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton

class ClickhouseStreamLoader(
    override val stream: DestinationStream
) : StreamLoader {

    override suspend fun start() {
        // Implementation for starting the stream loader
        // TODO: Implement
    }
}

@Singleton
class ClickhouseWriter: DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader =
        ClickhouseStreamLoader(stream)
}
