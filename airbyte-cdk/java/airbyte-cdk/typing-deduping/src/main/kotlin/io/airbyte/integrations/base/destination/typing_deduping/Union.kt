/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

/**
 * Represents a {type: [a, b, ...]} schema. This is theoretically equivalent to {oneOf: [{type: a},
 * {type: b}, ...]} but legacy normalization only handles the {type: [...]} schemas.
 *
 *
 * Eventually we should:
 *
 *  1. Announce a breaking change to handle both oneOf styles the same
 *  1. Test against some number of API sources to verify that they won't break badly
 *  1. Update [AirbyteType.fromJsonSchema] to parse both styles into
 * SupportedOneOf
 *  1. Delete UnsupportedOneOf
 *
 */
@JvmRecord
data class Union(val options: List<AirbyteType>) : AirbyteType {
    /**
     * This is a hack to handle weird schemas like {type: [object, string]}. If a stream's top-level
     * schema looks like this, we still want to be able to extract the object properties (i.e. treat it
     * as though the string option didn't exist).
     *
     * @throws IllegalArgumentException if we cannot extract columns from this schema
     */
    fun asColumns(): LinkedHashMap<String, AirbyteType> {
        val numObjectOptions = options.stream().filter { o: AirbyteType? -> o is Struct }.count()
        if (numObjectOptions > 1) {
            AirbyteType.LOGGER.error("Can't extract columns from a schema with multiple object options")
            return LinkedHashMap()
        }

        return options.stream().filter { o: AirbyteType? -> o is Struct }.findFirst()
                .map { o: AirbyteType -> (o as Struct).properties }
                .orElseGet {
                    AirbyteType.LOGGER.error("Can't extract columns from a schema with no object options")
                    LinkedHashMap()
                }
    }

    // Picks which type in a Union takes precedence
    fun chooseType(): AirbyteType {
        val comparator = Comparator.comparing { t: AirbyteType? ->
            if (t is Array) {
                -2
            } else if (t is Struct) {
                -1
            } else if (t is AirbyteProtocolType) {
                java.util.List.of(*AirbyteProtocolType.entries.toTypedArray()).indexOf(t)
            }
            Int.MAX_VALUE }

        return options.stream().min(comparator).orElse(AirbyteProtocolType.UNKNOWN)
    }

    override fun getTypeName(): String {
        return TYPE
    }

    companion object {
        const val TYPE: String = "UNION"
    }
}
