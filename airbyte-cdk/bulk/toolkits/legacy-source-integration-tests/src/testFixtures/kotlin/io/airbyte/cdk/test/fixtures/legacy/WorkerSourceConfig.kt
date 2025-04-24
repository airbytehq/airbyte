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
 * WorkerSourceConfig
 *
 * WorkerSourceConfig
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder("sourceId", "sourceConnectionConfiguration", "catalog", "state")
class WorkerSourceConfig : Serializable {
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
    @get:JsonProperty("sourceId")
    @set:JsonProperty("sourceId")
    @JsonProperty("sourceId")
    var sourceId: UUID? = null
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    @get:JsonProperty("sourceConnectionConfiguration")
    @set:JsonProperty("sourceConnectionConfiguration")
    @JsonProperty("sourceConnectionConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    var sourceConnectionConfiguration: JsonNode? = null
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

    fun withSourceId(sourceId: UUID?): WorkerSourceConfig {
        this.sourceId = sourceId
        return this
    }

    fun withSourceConnectionConfiguration(
        sourceConnectionConfiguration: JsonNode?
    ): WorkerSourceConfig {
        this.sourceConnectionConfiguration = sourceConnectionConfiguration
        return this
    }

    fun withCatalog(catalog: ConfiguredAirbyteCatalog?): WorkerSourceConfig {
        this.catalog = catalog
        return this
    }

    fun withState(state: State?): WorkerSourceConfig {
        this.state = state
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(WorkerSourceConfig::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("sourceId")
        sb.append('=')
        sb.append((if ((this.sourceId == null)) "<null>" else this.sourceId))
        sb.append(',')
        sb.append("sourceConnectionConfiguration")
        sb.append('=')
        sb.append(
            (if ((this.sourceConnectionConfiguration == null)) "<null>"
            else this.sourceConnectionConfiguration)
        )
        sb.append(',')
        sb.append("catalog")
        sb.append('=')
        sb.append((if ((this.catalog == null)) "<null>" else this.catalog))
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
        result = ((result * 31) + (if ((this.sourceId == null)) 0 else sourceId.hashCode()))
        result = ((result * 31) + (if ((this.state == null)) 0 else state.hashCode()))
        result =
            ((result * 31) +
                (if ((this.sourceConnectionConfiguration == null)) 0
                else sourceConnectionConfiguration.hashCode()))
        result = ((result * 31) + (if ((this.catalog == null)) 0 else catalog.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is WorkerSourceConfig) == false) {
            return false
        }
        val rhs = other
        return (((((this.sourceId === rhs.sourceId) ||
            ((this.sourceId != null) && (this.sourceId == rhs.sourceId))) &&
            ((this.state === rhs.state) || ((this.state != null) && state!!.equals(rhs.state)))) &&
            ((this.sourceConnectionConfiguration === rhs.sourceConnectionConfiguration) ||
                ((this.sourceConnectionConfiguration != null) &&
                    (this.sourceConnectionConfiguration == rhs.sourceConnectionConfiguration)))) &&
            ((this.catalog === rhs.catalog) ||
                ((this.catalog != null) && (this.catalog == rhs.catalog))))
    }

    companion object {
        private const val serialVersionUID = -9155072087909100892L
    }
}
