/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async.model

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import java.util.Objects

class PartialAirbyteStateMessage {
    @get:JsonProperty("type")
    @set:JsonProperty("type")
    @JsonProperty("type")
    var type: AirbyteStateMessage.AirbyteStateType? = null

    @get:JsonProperty("stream")
    @set:JsonProperty("stream")
    @JsonProperty("stream")
    var stream: PartialAirbyteStreamState? = null

    fun withType(type: AirbyteStateMessage.AirbyteStateType?): PartialAirbyteStateMessage {
        this.type = type
        return this
    }

    fun withStream(stream: PartialAirbyteStreamState?): PartialAirbyteStateMessage {
        this.stream = stream
        return this
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as PartialAirbyteStateMessage
        return type == that.type && stream == that.stream
    }

    override fun hashCode(): Int {
        return Objects.hash(type, stream)
    }

    override fun toString(): String {
        return "PartialAirbyteStateMessage{" + "type=" + type + ", stream=" + stream + '}'
    }
}
