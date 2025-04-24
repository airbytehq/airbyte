/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import java.io.Serializable

/**
 * StandardCheckConnectionOutput
 *
 * describes the result of a 'check connection' action.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder("status", "message")
class StandardCheckConnectionOutput : Serializable {
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
    @get:JsonProperty("status")
    @set:JsonProperty("status")
    @JsonProperty("status")
    var status: Status? = null

    @get:JsonProperty("message")
    @set:JsonProperty("message")
    @JsonProperty("message")
    var message: String? = null

    fun withStatus(status: Status?): StandardCheckConnectionOutput {
        this.status = status
        return this
    }

    fun withMessage(message: String?): StandardCheckConnectionOutput {
        this.message = message
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(StandardCheckConnectionOutput::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("status")
        sb.append('=')
        sb.append((if ((this.status == null)) "<null>" else this.status))
        sb.append(',')
        sb.append("message")
        sb.append('=')
        sb.append((if ((this.message == null)) "<null>" else this.message))
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
        result = ((result * 31) + (if ((this.message == null)) 0 else message.hashCode()))
        result = ((result * 31) + (if ((this.status == null)) 0 else status.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is StandardCheckConnectionOutput) == false) {
            return false
        }
        val rhs = other
        return (((this.message === rhs.message) ||
            ((this.message != null) && (this.message == rhs.message))) &&
            ((this.status == rhs.status) || ((this.status != null) && (this.status == rhs.status))))
    }

    enum class Status(private val value: String) {
        SUCCEEDED("succeeded"),
        FAILED("failed");

        override fun toString(): String {
            return this.value
        }

        @JsonValue
        fun value(): String {
            return this.value
        }

        companion object {
            private val CONSTANTS: MutableMap<String, Status> = HashMap()

            init {
                for (c in entries) {
                    CONSTANTS[c.value] = c
                }
            }

            @JsonCreator
            fun fromValue(value: String): Status {
                val constant = CONSTANTS[value]
                requireNotNull(constant) { value }
                return constant
            }
        }
    }

    companion object {
        private const val serialVersionUID = -6224403534620063521L
    }
}
