/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigInteger

/**
 * Mapper for nulling out integers that are out of range. The default behavior is to null out
 * integers that are outside the range of a 64-bit signed integer.
 */
class NullOutOfRangeIntegers(
    private val minValue: BigInteger = Long.MIN_VALUE.toBigInteger(),
    private val maxValue: BigInteger = Long.MAX_VALUE.toBigInteger()
) : AirbyteValueIdentityMapper() {
    override fun mapInteger(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        value as IntegerValue
        if (value.value < minValue || value.value > maxValue) {
            return nulledOut(
                IntegerType,
                context,
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
            )
        }
        return super.mapInteger(value, context)
    }
}
