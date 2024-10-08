/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.io.Serializable

sealed interface AirbyteType : Serializable

class NullType : AirbyteType

class StringType : AirbyteType

class BooleanType : AirbyteType

class IntegerType : AirbyteType

class NumberType : AirbyteType

class DateType : AirbyteType

data class TimestampType(val hasTimezone: Boolean) : AirbyteType

data class TimeType(val hasTimezone: Boolean) : AirbyteType

data class ArrayType(val items: FieldType) : AirbyteType

class ArrayTypeWithoutSchema : AirbyteType

data class ObjectType(val properties: LinkedHashMap<String, FieldType>) : AirbyteType

class ObjectTypeWithEmptySchema : AirbyteType

class ObjectTypeWithoutSchema : AirbyteType

data class UnionType(val options: List<AirbyteType>) : AirbyteType

data class UnknownType(val what: String) : AirbyteType

data class FieldType(val type: AirbyteType, val nullable: Boolean) : Serializable
