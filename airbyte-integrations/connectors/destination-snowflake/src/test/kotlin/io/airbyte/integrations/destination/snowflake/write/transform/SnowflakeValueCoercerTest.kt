/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeValueCoercerTest {

    @Test
    fun testMap() {
        val airbyteValue = mockk<EnrichedAirbyteValue>()
        val coercer = SnowflakeValueCoercer()
        val result = coercer.map(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testValidate() {
        val airbyteValue = mockk<EnrichedAirbyteValue>()
        val coercer = SnowflakeValueCoercer()
        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }
}
