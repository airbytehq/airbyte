package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.annotation.JsonCreator
import com.fasterxml.jackson.annotation.JsonValue

/**
 * ActorType
 *
 *
 * enum that describes different types of actors
 *
 */
enum class ActorType(private val value: String) {
    SOURCE("source"),
    DESTINATION("destination");

    override fun toString(): String {
        return this.value
    }

    @JsonValue
    fun value(): String {
        return this.value
    }

    companion object {
        private val CONSTANTS: MutableMap<String, ActorType> = HashMap()

        init {
            for (c in entries) {
                CONSTANTS[c.value] = c
            }
        }

        @JsonCreator
        fun fromValue(value: String): ActorType {
            val constant = CONSTANTS[value]
            requireNotNull(constant) { value }
            return constant
        }
    }
}
