package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamLoader

class ShelbyStreamLoader(override val stream: DestinationStream) : StreamLoader {
}
