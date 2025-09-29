package io.airbyte.cdk.load.writer

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader

class DeclarativeStreamLoader(override val stream: DestinationStream) : StreamLoader

class DeclarativeWriter : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return DeclarativeStreamLoader(stream)
    }
}
