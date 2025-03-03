/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.*
import java.io.Serializable

/**
 * OperatorNormalization
 *
 * Settings for a normalization operator
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder("option")
class OperatorNormalization : Serializable {
    @get:JsonProperty("option")
    @set:JsonProperty("option")
    @JsonProperty("option")
    var option: Option? = null

    fun withOption(option: Option?): OperatorNormalization {
        this.option = option
        return this
    }

    override fun toString(): String {
        val sb = StringBuilder()
        sb.append(OperatorNormalization::class.java.name)
            .append('@')
            .append(Integer.toHexString(System.identityHashCode(this)))
            .append('[')
        sb.append("option")
        sb.append('=')
        sb.append((if ((this.option == null)) "<null>" else this.option))
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
        result = ((result * 31) + (if ((this.option == null)) 0 else option.hashCode()))
        return result
    }

    override fun equals(other: Any?): Boolean {
        if (other === this) {
            return true
        }
        if ((other is OperatorNormalization) == false) {
            return false
        }
        val rhs = other
        return ((this.option == rhs.option) ||
            ((this.option != null) && (this.option == rhs.option)))
    }

    enum class Option(private val value: String) {
        BASIC("basic");

        override fun toString(): String {
            return this.value
        }

        @JsonValue
        fun value(): String {
            return this.value
        }

        companion object {
            private val CONSTANTS: MutableMap<String, Option> = HashMap()

            init {
                for (c in entries) {
                    CONSTANTS[c.value] = c
                }
            }

            @JsonCreator
            fun fromValue(value: String): Option {
                val constant = CONSTANTS[value]
                requireNotNull(constant) { value }
                return constant
            }
        }
    }

    companion object {
        private const val serialVersionUID = 7237719528722425365L
    }
}
