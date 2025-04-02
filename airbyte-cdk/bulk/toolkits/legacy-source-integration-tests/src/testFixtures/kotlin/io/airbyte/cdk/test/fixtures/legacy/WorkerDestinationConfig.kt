/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import java.io.Serializable
import java.util.*

/**
 * WorkerDestinationConfig
 *
 * WorkerDestinationConfig
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder(
    "destinationId",
    "destinationConnectionConfiguration",
    "catalog",
    "connectionId",
    "state"
)
class WorkerDestinationConfig : Serializable {
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    @get:JsonProperty("destinationId")
    @set:JsonProperty("destinationId")
    @JsonProperty("destinationId")
    var destinationId: UUID? = null
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    @get:JsonProperty("destinationConnectionConfiguration")
    @set:JsonProperty("destinationConnectionConfiguration")
    @JsonProperty("destinationConnectionConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    var destinationConnectionConfiguration: JsonNode? = null
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    @get:JsonProperty("catalog")
    @set:JsonProperty("catalog")
    @JsonProperty("catalog")
    var catalog: ConfiguredAirbyteCatalog? = null
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    /**
     *
     * (Required)
     */
    @get:JsonProperty("connectionId")
    @set:JsonProperty("connectionId")
    @JsonProperty("connectionId")
    var connectionId: UUID? = null
    /**
     * State
     *
     * information output by the connection.
     */
    /**
     * State
     *
     * information output by the connection.
     */
    /**
     * State
     *
     * information output by the connection.
     */
    @get:JsonProperty("state")
    @set:JsonProperty("state")
    @JsonProperty("state")
    @JsonPropertyDescription("information output by the connection.")
    var state: State? = null

    fun withDestinationId(destinationId: UUID?): WorkerDestinationConfig {
        this.destinationId = destinationId
        return this
    }

    fun withDestinationConnectionConfiguration(
        destinationConnectionConfiguration: JsonNode?
    ): WorkerDestinationConfig {
        this.destinationConnectionConfiguration = destinationConnectionConfiguration
        return this
    }

    fun withCatalog(catalog: ConfiguredAirbyteCatalog?): WorkerDestinationConfig {
        this.catalog = catalog
        return this
    }

    fun withConnectionId(connectionId: UUID?): WorkerDestinationConfig {
        this.connectionId = connectionId
        return this
    }

    fun withState(state: State?): WorkerDestinationConfig {
        this.state = state
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(WorkerDestinationConfig::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("destinationId")
        sb.append('=')
        sb.append((if ((this.destinationId == null)) "<null>" else this.destinationId))
        sb.append(',')
        sb.append("destinationConnectionConfiguration")
        sb.append('=')
        sb.append(
            (if ((this.destinationConnectionConfiguration == null)) "<null>"
            else this.destinationConnectionConfiguration)
        )
        sb.append(',')
        sb.append("catalog")
        sb.append('=')
        sb.append((if ((this.catalog == null)) "<null>" else this.catalog))
        sb.append(',')
        sb.append("connectionId")
        sb.append('=')
        sb.append((if ((this.connectionId == null)) "<null>" else this.connectionId))
        sb.append(',')
        sb.append("state")
        sb.append('=')
        sb.append((if ((this.state == null)) "<null>" else this.state))
        sb.append(',')
        if (sb[sb.length - 1] == ',') {
            sb.setCharAt((sb.length - 1), ']')
        } else {
            sb.append(']')
        }
        return sb.toString()
    }

    override fun hashCode(): Int {
        var result = 1
        result = ((result * 31) + (if ((this.connectionId == null)) 0 else connectionId.hashCode()))
        result = ((result * 31) + (if ((this.state == null)) 0 else state.hashCode()))
        result =
            ((result * 31) + (if ((this.destinationId == null)) 0 else destinationId.hashCode()))
        result =
            ((result * 31) +
                (if ((this.destinationConnectionConfiguration == null)) 0
                else destinationConnectionConfiguration.hashCode()))
        result = ((result * 31) + (if ((this.catalog == null)) 0 else catalog.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is WorkerDestinationConfig) == false) {
            return false
        }
        val rhs = other
        return ((((((this.connectionId === rhs.connectionId) ||
            ((this.connectionId != null) && (this.connectionId == rhs.connectionId))) &&
            ((this.state === rhs.state) || ((this.state != null) && state!!.equals(rhs.state)))) &&
            ((this.destinationId === rhs.destinationId) ||
                ((this.destinationId != null) && (this.destinationId == rhs.destinationId)))) &&
            ((this.destinationConnectionConfiguration === rhs.destinationConnectionConfiguration) ||
                ((this.destinationConnectionConfiguration != null) &&
                    (this.destinationConnectionConfiguration ==
                        rhs.destinationConnectionConfiguration)))) &&
            ((this.catalog === rhs.catalog) ||
                ((this.catalog != null) && (this.catalog == rhs.catalog))))
    }

    companion object {
        private const val serialVersionUID = 4991217442954865951L
    }
}
