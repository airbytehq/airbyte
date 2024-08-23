package io.airbyte.integrations.base.destination.experimental

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.Command
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog

class DockerizedDestination(
    command: Command,
    config: JsonNode,
    catalog: ConfiguredAirbyteCatalog,
): DestinationProcess {
    init {
        // launch a docker container...
    }

    override fun sendMessage(message: AirbyteMessage) {
        // push a message to the docker process' stdin
        TODO("Not yet implemented")
    }

    override fun readMessages(): List<AirbyteMessage> {
        // read everything from the process' stdout
        TODO("Not yet implemented")
    }

    override fun waitUntilDone() {
        // close stdin, wait until process exits
        TODO("Not yet implemented")
    }
}
