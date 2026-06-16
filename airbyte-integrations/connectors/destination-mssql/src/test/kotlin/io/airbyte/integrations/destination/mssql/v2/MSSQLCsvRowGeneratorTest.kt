/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class MSSQLCsvRowGeneratorTest {

    @Test
    fun `boolean true serializes to 1 for BIT column regardless of validation`() {
        assertEquals(BigInteger.ONE, BooleanValue(true).toMssqlCsvValue())
    }

    @Test
    fun `boolean false serializes to 0 for BIT column regardless of validation`() {
        assertEquals(BigInteger.ZERO, BooleanValue(false).toMssqlCsvValue())
    }

    @Test
    fun `null and NullValue serialize to empty string`() {
        val nullValue: AirbyteValue? = null
        assertEquals("", nullValue.toMssqlCsvValue())
        assertEquals("", NullValue.toMssqlCsvValue())
    }

    @Test
    fun `non-boolean values pass through unchanged`() {
        assertEquals("hello", StringValue("hello").toMssqlCsvValue())
        assertEquals(BigInteger.valueOf(42), IntegerValue(42L).toMssqlCsvValue())
    }
}
