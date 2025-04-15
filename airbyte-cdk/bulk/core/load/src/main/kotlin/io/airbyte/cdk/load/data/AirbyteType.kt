/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.JsonNode

sealed interface AirbyteType {
    /**
     * Utility method for database/warehouse destinations, which assume that the top-level schema is
     * an object.
     */
    fun getProperties(): LinkedHashMap<String, FieldType> {
        return linkedMapOf()
    }

    val isObject: Boolean
        get() = false
    val isArray: Boolean
        get() = false
}

data object StringType : AirbyteType

data object BooleanType : AirbyteType

data object IntegerType : AirbyteType

data object NumberType : AirbyteType

data object DateType : AirbyteType

data object TimestampTypeWithTimezone : AirbyteType

data object TimestampTypeWithoutTimezone : AirbyteType

data object TimeTypeWithTimezone : AirbyteType

data object TimeTypeWithoutTimezone : AirbyteType

data class ArrayType(val items: FieldType) : AirbyteType {
    override val isArray = true
}

data object ArrayTypeWithoutSchema : AirbyteType {
    override val isArray = true
}

data class ObjectType(val properties: LinkedHashMap<String, FieldType>) : AirbyteType {
    override fun getProperties(): LinkedHashMap<String, FieldType> {
        return properties
    }

    override val isObject = true
}

data object ObjectTypeWithEmptySchema : AirbyteType {
    override val isObject = true
}

data object ObjectTypeWithoutSchema : AirbyteType {
    override val isObject = true
}

data class UnionType(
    val options: Set<AirbyteType>,
    val isLegacyUnion: Boolean,
) : AirbyteType {
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

data class UnknownType(val schema: JsonNode) : AirbyteType

data class FieldType(val type: AirbyteType, val nullable: Boolean)
