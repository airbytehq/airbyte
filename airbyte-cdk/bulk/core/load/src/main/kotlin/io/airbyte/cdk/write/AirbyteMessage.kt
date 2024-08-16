package io.airbyte.cdk.write

import com.fasterxml.jackson.annotation.JsonCreator
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.write.DestinationMessage.*

/**
 * Bespoke envelope for AirbyteMessages.
 *
 * Right now just a dummy for prototyping, but in practice should represent the
 * messages entering the destination.
 */
enum class AirbyteMessageType {
    RECORD,
    STREAM_COMPLETE
}

class AirbyteMessage @JsonCreator constructor(
    @JsonProperty("stream") val stream: Stream,
    @JsonProperty("type") val type: AirbyteMessageType
) {
    @JsonProperty("data")
    val data: JsonNode? = null

    var sizeBytes: Long = 0L

    companion object {
        fun fromSerialized(serialized: String): AirbyteMessage {
            val message = ObjectMapper().readValue(serialized, AirbyteMessage::class.java)
            message.sizeBytes = serialized.length.toLong()
            return message
        }
    }

    fun record(index: Long): DestinationRecord {
        return DestinationRecord(stream, index, sizeBytes, data)
    }
}
