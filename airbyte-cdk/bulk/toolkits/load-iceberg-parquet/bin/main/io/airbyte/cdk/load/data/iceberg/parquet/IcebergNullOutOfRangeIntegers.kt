/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueIdentityMapper
import io.airbyte.cdk.load.data.NullOutOfRangeIntegers
import java.math.BigInteger

/**
 * Iceberg wants to write objects/unions as JSON strings, but arrays as strongly-typed. Therefore,
 * we need to handle top-level ints, and arrays of ints, but should ignore ints inside objects, and
 * ints inside unions.
 */
class IcebergNullOutOfRangeIntegers(
    minValue: BigInteger = Long.MIN_VALUE.toBigInteger(),
    maxValue: BigInteger = Long.MAX_VALUE.toBigInteger()
) :
    AirbyteValueIdentityMapper(
        recurseIntoObjects = false,
        recurseIntoArrays = true,
        recurseIntoUnions = false,
    ) {
    private val delegate = NullOutOfRangeIntegers(minValue = minValue, maxValue = maxValue)

    override fun mapInteger(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        return delegate.mapInteger(value, context)
    }
}
