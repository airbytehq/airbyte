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
import java.util.*

/**
 * StandardCheckConnectionInput
 *
 * information required for connection.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder("actorType", "actorId", "connectionConfiguration")
class StandardCheckConnectionInput : Serializable {
    /**
     * ActorType
     *
     * enum that describes different types of actors
     */
    /**
     * ActorType
     *
     * enum that describes different types of actors
     */
    /**
     * ActorType
     *
     * enum that describes different types of actors
     */
    @get:JsonProperty("actorType")
    @set:JsonProperty("actorType")
    @JsonProperty("actorType")
    @JsonPropertyDescription("enum that describes different types of actors")
    var actorType: ActorType? = null
    /** The ID of the actor being checked, so we can persist config updates */
    /** The ID of the actor being checked, so we can persist config updates */
    /** The ID of the actor being checked, so we can persist config updates */
    @get:JsonProperty("actorId")
    @set:JsonProperty("actorId")
    @JsonProperty("actorId")
    @JsonPropertyDescription("The ID of the actor being checked, so we can persist config updates")
    var actorId: UUID? = null
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    /** Integration specific blob. Must be a valid JSON string. (Required) */
    @get:JsonProperty("connectionConfiguration")
    @set:JsonProperty("connectionConfiguration")
    @JsonProperty("connectionConfiguration")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    var connectionConfiguration: JsonNode? = null

    fun withActorType(actorType: ActorType?): StandardCheckConnectionInput {
        this.actorType = actorType
        return this
    }

    fun withActorId(actorId: UUID?): StandardCheckConnectionInput {
        this.actorId = actorId
        return this
    }

    fun withConnectionConfiguration(
        connectionConfiguration: JsonNode?
    ): StandardCheckConnectionInput {
        this.connectionConfiguration = connectionConfiguration
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(StandardCheckConnectionInput::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("actorType")
        sb.append('=')
        sb.append((if ((this.actorType == null)) "<null>" else this.actorType))
        sb.append(',')
        sb.append("actorId")
        sb.append('=')
        sb.append((if ((this.actorId == null)) "<null>" else this.actorId))
        sb.append(',')
        sb.append("connectionConfiguration")
        sb.append('=')
        sb.append(
            (if ((this.connectionConfiguration == null)) "<null>" else this.connectionConfiguration)
        )
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
        result = ((result * 31) + (if ((this.actorType == null)) 0 else actorType.hashCode()))
        result = ((result * 31) + (if ((this.actorId == null)) 0 else actorId.hashCode()))
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
        if ((other is StandardCheckConnectionInput) == false) {
            return false
        }
        val rhs = other
        return ((((this.actorType == rhs.actorType) ||
            ((this.actorType != null) && (this.actorType == rhs.actorType))) &&
            ((this.actorId === rhs.actorId) ||
                ((this.actorId != null) && (this.actorId == rhs.actorId)))) &&
            ((this.connectionConfiguration === rhs.connectionConfiguration) ||
                ((this.connectionConfiguration != null) &&
                    (this.connectionConfiguration == rhs.connectionConfiguration))))
    }

    companion object {
        private const val serialVersionUID = 8678033101171962295L
    }
}
