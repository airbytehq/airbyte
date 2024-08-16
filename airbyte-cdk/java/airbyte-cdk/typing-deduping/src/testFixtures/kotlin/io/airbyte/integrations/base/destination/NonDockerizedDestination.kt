package io.airbyte.integrations.base.destination

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.Command
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog

class NonDockerizedDestination(
    command: Command,
    config: JsonNode,
    catalog: ConfiguredAirbyteCatalog,
    // some other param to get whatever code we're actually running,
    // i.e. equivalent to io.airbyte.integrations.base.destination.Destination
): Destination {
    init {
        // invoke whatever CDK stuff exists to run a destination connector
        // but use some reasonable interface instead of stdin/stdout
    }

    override fun sendMessage(message: AirbyteMessage) {
        TODO("Not yet implemented")
    }

    override fun readMessages(): List<AirbyteMessage> {
        TODO("Not yet implemented")
    }

    override fun waitUntilDone() {
        // send a "stdin closed" signal
        TODO("Not yet implemented")
    }
}
