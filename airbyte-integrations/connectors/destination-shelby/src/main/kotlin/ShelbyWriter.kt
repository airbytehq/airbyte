package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton

@Singleton
class ShelbyWriter : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return ShelbyStreamLoader(stream)
    }
}
