package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.databind.JsonNode
import java.io.Serializable

/**
 * State
 *
 *
 * information output by the connection.
 *
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder(
    "state"
)
class State : Serializable {
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    /**
     * Integration specific blob. Must be a valid JSON string.
     * (Required)
     *
     */
    @get:JsonProperty("state")
    @set:JsonProperty("state")
    @JsonProperty("state")
    @JsonPropertyDescription("Integration specific blob. Must be a valid JSON string.")
    var state: JsonNode? = null

    fun withState(state: JsonNode?): State {
        this.state = state
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(State::class.java.name).append('@').append(
            Integer.toHexString(
                System.identityHashCode(
                    this
                )
            )
        ).append('[')
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
        result = ((result * 31) + (if ((this.state == null)) 0 else state.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is State) == false) {
            return false
        }
        val rhs = other
        return ((this.state === rhs.state) || ((this.state != null) && (this.state == rhs.state)))
    }

    companion object {
        private const val serialVersionUID = -2756677927650777185L
    }
}
