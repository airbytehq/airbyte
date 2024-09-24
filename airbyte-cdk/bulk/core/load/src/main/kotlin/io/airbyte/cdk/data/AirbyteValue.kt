/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.data

import java.math.BigDecimal

sealed interface AirbyteValue

data object NullValue : AirbyteValue

@JvmInline value class StringValue(val value: String) : AirbyteValue

@JvmInline value class BooleanValue(val value: Boolean) : AirbyteValue

@JvmInline value class IntegerValue(val value: Long) : AirbyteValue

@JvmInline value class NumberValue(val value: BigDecimal) : AirbyteValue

@JvmInline value class DateValue(val value: String) : AirbyteValue

@JvmInline value class TimestampValue(val value: String) : AirbyteValue

@JvmInline value class TimeValue(val value: String) : AirbyteValue

@JvmInline value class ArrayValue(val values: List<AirbyteValue>) : AirbyteValue

@JvmInline value class ObjectValue(val values: LinkedHashMap<String, AirbyteValue>) : AirbyteValue

@JvmInline value class UnknownValue(val what: String) : AirbyteValue
