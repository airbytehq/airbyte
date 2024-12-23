/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.ValueTestBuilder
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigInteger
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class NullOutOfRangeIntegersTest {
    @Test
    fun testDefaultBehavior() {
        val (valueIn, schemaIn, expectedValue) =
            ValueTestBuilder<Root>()
                .with(IntegerValue(150), IntegerType, nullable = true)
                .with(
                    IntegerValue(BigInteger("123456789012345678901234567890")),
                    IntegerType,
                    NullValue,
                    nameOverride = "big_integer",
                    nullable = true
                )
                .build()
        val (actualValue, changes) = NullOutOfRangeIntegers().map(valueIn, schemaIn)
        Assertions.assertEquals(expectedValue, actualValue)
        Assertions.assertEquals(1, changes.size)
        Assertions.assertEquals(
            Meta.Change(
                "big_integer",
                Change.NULLED,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            ),
            changes[0]
        )
    }

    @Test
    fun testRestrictiveBehavior() {
        val minValue = BigInteger("100")
        val maxValue = BigInteger("200")
        val (valueIn, schemaIn, expectedValue) =
            ValueTestBuilder<Root>()
                .with(IntegerValue(150), IntegerType, nullable = true)
                .with(
                    IntegerValue(10),
                    IntegerType,
                    NullValue,
                    nameOverride = "too_small",
                    nullable = true
                )
                .with(
                    IntegerValue(300),
                    IntegerType,
                    NullValue,
                    nameOverride = "too_big",
                    nullable = true
                )
                .build()
        val (actualValue, changes) =
            NullOutOfRangeIntegers(minValue, maxValue).map(valueIn, schemaIn)
        Assertions.assertEquals(expectedValue, actualValue)
        Assertions.assertEquals(
            setOf(
                Meta.Change(
                    "too_small",
                    Change.NULLED,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                ),
                Meta.Change(
                    "too_big",
                    Change.NULLED,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                ),
                changes[1]
            ),
            changes.toSet()
        )
    }
}
