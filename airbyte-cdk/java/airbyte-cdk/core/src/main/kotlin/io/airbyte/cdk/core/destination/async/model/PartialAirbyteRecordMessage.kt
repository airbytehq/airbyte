package io.airbyte.cdk.core.destination.async.model

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.Objects

class PartialAirbyteRecordMessage {

    @JsonProperty("namespace")
    var namespace: String? = null

    @JsonProperty("stream")
    var stream: String? = null

    @JsonProperty("data")
    var data: JsonNode? = null

    @JsonProperty("emitted_at")
    @JsonPropertyDescription("when the data was emitted from the source. epoch in millisecond.")
    var emittedAt: Long = 0

    fun withNamespace(namespace: String?): PartialAirbyteRecordMessage {
        this.namespace = namespace
        return this
    }

    fun withStream(stream: String?): PartialAirbyteRecordMessage {
        this.stream = stream
        return this
    }

    fun withData(data: JsonNode?): PartialAirbyteRecordMessage {
        this.data = data
        return this
    }

    fun withEmittedAt(emittedAt: Long): PartialAirbyteRecordMessage {
        this.emittedAt = emittedAt
        return this
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) {
            return true
        }
        if (other == null || javaClass != other.javaClass) {
            return false
        }
        val that = other as PartialAirbyteRecordMessage
        return namespace == that.namespace && stream == that.stream && emittedAt == that.emittedAt
    }

    override fun hashCode(): Int {
        return Objects.hash(namespace, stream, emittedAt)
    }

    override fun toString(): String {
        return "PartialAirbyteRecordMessage{" +
                "namespace='" + namespace + '\'' +
                ", stream='" + stream + '\'' +
                ", emittedAt='" + emittedAt + '\'' +
                '}'
    }

    fun getStreamDescriptor(): StreamDescriptor {
        return StreamDescriptor().withName(stream).withNamespace(namespace)
    }
}