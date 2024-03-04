package io.airbyte.cdk.core.destination.async.model

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.Objects

class PartialAirbyteStreamState {

    @JsonProperty("stream_descriptor")
    var streamDescriptor: StreamDescriptor? = null

    fun withStreamDescriptor(streamDescriptor: StreamDescriptor?): PartialAirbyteStreamState {
        this.streamDescriptor = streamDescriptor
        return this
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as PartialAirbyteStreamState
        return streamDescriptor == that.streamDescriptor
    }

    override fun hashCode(): Int {
        return Objects.hash(streamDescriptor)
    }

    override fun toString(): String {
        return "PartialAirbyteStreamState{" +
                "streamDescriptor=" + streamDescriptor +
                '}'
    }
}