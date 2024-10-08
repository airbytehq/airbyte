/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

sealed interface AirbyteType

data object NullType : AirbyteType

data object StringType : AirbyteType

data object BooleanType : AirbyteType

data object IntegerType : AirbyteType

data object NumberType : AirbyteType

data object DateType : AirbyteType

data class TimestampType(val hasTimezone: Boolean) : AirbyteType

data class TimeType(val hasTimezone: Boolean) : AirbyteType

data class ArrayType(val items: FieldType) : AirbyteType

data object ArrayTypeWithoutSchema : AirbyteType

data class ObjectType(val properties: LinkedHashMap<String, FieldType>) : AirbyteType

data object ObjectTypeWithEmptySchema : AirbyteType

data object ObjectTypeWithoutSchema : AirbyteType

data class UnionType(val options: List<AirbyteType>) : AirbyteType

data class UnknownType(val what: String) : AirbyteType

data class FieldType(val type: AirbyteType, val nullable: Boolean)
