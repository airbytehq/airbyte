/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.databind.JsonNode
import java.io.Serializable

/**
 * StandardDiscoverCatalogInput
 *
 * information required for connection.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder("connectionConfiguration", "sourceId", "connectorVersion", "configHash")
class StandardDiscoverCatalogInput : Serializable {
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    @get:JsonProperty("connectionConfiguration")
    @set:JsonProperty("connectionConfiguration")
    @JsonProperty("connectionConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    var connectionConfiguration: JsonNode? = null
    /** The ID of the source being discovered, so we can persist the result (Required) */
    /** The ID of the source being discovered, so we can persist the result (Required) */
    /** The ID of the source being discovered, so we can persist the result (Required) */
    @get:JsonProperty("sourceId")
    @set:JsonProperty("sourceId")
    @JsonProperty("sourceId")
    @JsonPropertyDescription("The ID of the source being discovered, so we can persist the result")
    var sourceId: String? = null
    /** Connector version, so we can persist the result (Required) */
    /** Connector version, so we can persist the result (Required) */
    /** Connector version, so we can persist the result (Required) */
    @get:JsonProperty("connectorVersion")
    @set:JsonProperty("connectorVersion")
    @JsonProperty("connectorVersion")
    @JsonPropertyDescription("Connector version, so we can persist the result")
    var connectorVersion: String? = null
    /** Config hash, so we can persist the result (Required) */
    /** Config hash, so we can persist the result (Required) */
    /** Config hash, so we can persist the result (Required) */
    @get:JsonProperty("configHash")
    @set:JsonProperty("configHash")
    @JsonProperty("configHash")
    @JsonPropertyDescription("Config hash, so we can persist the result")
    var configHash: String? = null

    fun withConnectionConfiguration(
        connectionConfiguration: JsonNode?
    ): StandardDiscoverCatalogInput {
        this.connectionConfiguration = connectionConfiguration
        return this
    }

    fun withSourceId(sourceId: String?): StandardDiscoverCatalogInput {
        this.sourceId = sourceId
        return this
    }

    fun withConnectorVersion(connectorVersion: String?): StandardDiscoverCatalogInput {
        this.connectorVersion = connectorVersion
        return this
    }

    fun withConfigHash(configHash: String?): StandardDiscoverCatalogInput {
        this.configHash = configHash
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(StandardDiscoverCatalogInput::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("connectionConfiguration")
        sb.append('=')
        sb.append(
            (if ((this.connectionConfiguration == null)) "<null>" else this.connectionConfiguration)
        )
        sb.append(',')
        sb.append("sourceId")
        sb.append('=')
        sb.append((if ((this.sourceId == null)) "<null>" else this.sourceId))
        sb.append(',')
        sb.append("connectorVersion")
        sb.append('=')
        sb.append((if ((this.connectorVersion == null)) "<null>" else this.connectorVersion))
        sb.append(',')
        sb.append("configHash")
        sb.append('=')
        sb.append((if ((this.configHash == null)) "<null>" else this.configHash))
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
        result =
            ((result * 31) +
                (if ((this.connectorVersion == null)) 0 else connectorVersion.hashCode()))
        result = ((result * 31) + (if ((this.configHash == null)) 0 else configHash.hashCode()))
        result =
            ((result * 31) +
                (if ((this.connectionConfiguration == null)) 0
                else connectionConfiguration.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is StandardDiscoverCatalogInput) == false) {
            return false
        }
        val rhs = other
        return (((((this.sourceId === rhs.sourceId) ||
            ((this.sourceId != null) && (this.sourceId == rhs.sourceId))) &&
            ((this.connectorVersion === rhs.connectorVersion) ||
                ((this.connectorVersion != null) &&
                    (this.connectorVersion == rhs.connectorVersion)))) &&
            ((this.configHash === rhs.configHash) ||
                ((this.configHash != null) && (this.configHash == rhs.configHash)))) &&
            ((this.connectionConfiguration === rhs.connectionConfiguration) ||
                ((this.connectionConfiguration != null) &&
                    (this.connectionConfiguration == rhs.connectionConfiguration))))
    }

    companion object {
        private const val serialVersionUID = 6835276481871177055L
    }
}
