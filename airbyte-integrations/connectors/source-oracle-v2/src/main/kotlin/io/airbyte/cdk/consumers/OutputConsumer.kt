package io.airbyte.cdk.consumers

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import jakarta.inject.Singleton
import java.util.function.Consumer

/** Emits the [AirbyteMessage] instances produced by the connector. */
fun interface OutputConsumer : Consumer<AirbyteMessage>

/** Default implementation of [OutputConsumer]. */
@Singleton
class StdoutOutputConsumer : OutputConsumer {
    override fun accept(airbyteMessage: AirbyteMessage) {
        val json: String = Jsons.serialize(airbyteMessage)
        synchronized(this) {
            println(json)
        }
    }
}
