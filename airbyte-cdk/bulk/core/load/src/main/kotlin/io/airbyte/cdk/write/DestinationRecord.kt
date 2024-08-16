package io.airbyte.cdk.write

import com.fasterxml.jackson.databind.JsonNode
import javax.print.attribute.standard.Destination

/**
 * Dummy record for prototyping
 */

sealed class DestinationMessage {
    data class DestinationRecord(
        val stream: Stream,
        val index: Long,
        val sizeBytes: Long,
        val data: JsonNode? = null
    ) : DestinationMessage()

    data class EndOfStream(val stream: Stream) : DestinationMessage()
    data object TimeOut : DestinationMessage()
}
