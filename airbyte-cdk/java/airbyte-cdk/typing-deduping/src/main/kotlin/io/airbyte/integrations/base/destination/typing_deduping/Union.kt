/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.github.oshai.kotlinlogging.KotlinLogging

private val LOGGER = KotlinLogging.logger {}
/**
 * Represents a {type: [a, b, ...]} schema. This is theoretically equivalent to {oneOf: [{type: a},
 * {type: b}, ...]} but legacy normalization only handles the {type: [...]} schemas.
 *
 * Eventually we should:
 *
 * 1. Announce a breaking change to handle both oneOf styles the same
 * 1. Test against some number of API sources to verify that they won't break badly
 * 1. Update [AirbyteType.fromJsonSchema] to parse both styles into SupportedOneOf
 * 1. Delete UnsupportedOneOf
 */
data class Union(val options: List<AirbyteType>) : AirbyteType {
    override val typeName: String = TYPE

    /**
     * This is a hack to handle weird schemas like {type: [object, string]}. If a stream's top-level
     * schema looks like this, we still want to be able to extract the object properties (i.e. treat
     * it as though the string option didn't exist).
     *
     * @throws IllegalArgumentException if we cannot extract columns from this schema
     */
    fun asColumns(): LinkedHashMap<String, AirbyteType> {
        LOGGER.warn { "asColumns options=$options" }
        val numObjectOptions = options.filterIsInstance<Struct>().count()
        if (numObjectOptions > 1) {
            LOGGER.error { "Can't extract columns from a schema with multiple object options" }
            return LinkedHashMap()
        }

        var retVal: LinkedHashMap<String, AirbyteType>
        try {
            retVal = options.filterIsInstance<Struct>().first().properties
        } catch (_: NoSuchElementException) {
            LOGGER.error { "Can't extract columns from a schema with no object options" }
            retVal = LinkedHashMap()
        }
        LOGGER.warn { "asColumns retVal=$retVal" }
        return retVal
    }

    // Picks which type in a Union takes precedence
    fun chooseType(): AirbyteType {
        if (options.isEmpty()) {
            return AirbyteProtocolType.UNKNOWN
        }

        return options.minBy {
            when (it) {
                is Array -> -2
                is Struct -> -1
                is AirbyteProtocolType -> it.ordinal
                else -> Int.MAX_VALUE
            }
        }
    }

    companion object {
        const val TYPE: String = "UNION"
    }
}
