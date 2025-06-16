/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

sealed class AirbyteType {
    /**
     * Utility method for database/warehouse destinations, which assume that the top-level schema is
     * an object.
     */
    open fun asColumns(): LinkedHashMap<String, FieldType> {
        return linkedMapOf()
    }

    open val isObject: Boolean = false
    open val isArray: Boolean = false
}

data object StringType : AirbyteType()

data object BooleanType : AirbyteType()

data object IntegerType : AirbyteType()

data object NumberType : AirbyteType()

data object DateType : AirbyteType()

data object TimestampTypeWithTimezone : AirbyteType()

data object TimestampTypeWithoutTimezone : AirbyteType()

data object TimeTypeWithTimezone : AirbyteType()

data object TimeTypeWithoutTimezone : AirbyteType()

data class ArrayType(val items: FieldType) : AirbyteType() {
    override val isArray = true
}

data object ArrayTypeWithoutSchema : AirbyteType() {
    override val isArray = true
}

data class ObjectType(
    val properties: LinkedHashMap<String, FieldType>,
    val additionalProperties: Boolean? = null,
    val required: List<String> = emptyList<String>()
) : AirbyteType() {
    override fun asColumns(): LinkedHashMap<String, FieldType> {
        return properties
    }

    override val isObject = true
}

data object ObjectTypeWithEmptySchema : AirbyteType() {
    override val isObject = true
}

data object ObjectTypeWithoutSchema : AirbyteType() {
    override val isObject = true
}

data class UnionType(
    val options: Set<AirbyteType>,
    val isLegacyUnion: Boolean,
) : AirbyteType() {
    /**
     * This is a hack to handle weird schemas like {type: [object, string]}. If a stream's top-level
     * schema looks like this, we still want to be able to extract the object properties (i.e. treat
     * it as though the string option didn't exist).
     *
     * @throws IllegalArgumentException if we cannot extract columns from this schema
     */
    override fun asColumns(): LinkedHashMap<String, FieldType> {
        logger.warn { "asColumns options=$options" }
        val numObjectOptions = options.count { it.isObject }
        if (numObjectOptions > 1) {
            logger.error { "Can't extract columns from a schema with multiple object options" }
            return LinkedHashMap()
        }

        var retVal: LinkedHashMap<String, FieldType>
        try {
            retVal = options.first { it.isObject }.asColumns()
        } catch (_: NoSuchElementException) {
            logger.error { "Can't extract columns from a schema with no object options" }
            retVal = LinkedHashMap()
        }
        logger.warn { "Union.asColumns retVal=$retVal" }
        return retVal
    }

    /**
     * This matches legacy behavior. Some destinations handle legacy unions by choosing the "best"
     * type from amongst the options. This is... not great, but it would be painful to change.
     */
    fun chooseType(): AirbyteType {
        check(isLegacyUnion) { "Cannot chooseType for a non-legacy union type" }
        if (options.isEmpty()) {
            return UnknownType(Jsons.createObjectNode())
        }
        return options.minBy {
            when (it) {
                is ArrayType,
                ArrayTypeWithoutSchema -> -2
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> -1
                StringType -> 0
                DateType -> 1
                TimeTypeWithoutTimezone -> 2
                TimeTypeWithTimezone -> 3
                TimestampTypeWithoutTimezone -> 4
                TimestampTypeWithTimezone -> 5
                NumberType -> 6
                IntegerType -> 7
                BooleanType -> 8
                is UnknownType -> 9
                is UnionType -> Int.MAX_VALUE
            }
        }
    }

    companion object {
        fun of(options: Set<AirbyteType>, isLegacyUnion: Boolean = false): AirbyteType {
            if (options.size == 1) {
                return options.first()
            }
            return UnionType(options, isLegacyUnion)
        }

        fun of(options: List<AirbyteType>, isLegacyUnion: Boolean = false): AirbyteType =
            of(options.toSet(), isLegacyUnion)

        fun of(vararg options: AirbyteType, isLegacyUnion: Boolean = false): AirbyteType =
            of(options.toSet(), isLegacyUnion)
    }
}

data class UnknownType(val schema: JsonNode) : AirbyteType()

data class FieldType(val type: AirbyteType, val nullable: Boolean)
