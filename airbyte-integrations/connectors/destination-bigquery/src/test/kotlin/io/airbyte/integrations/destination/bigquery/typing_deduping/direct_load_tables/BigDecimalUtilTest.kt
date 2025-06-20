/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping.direct_load_tables

import io.airbyte.integrations.destination.bigquery.formatter.BigDecimalUtil
import io.airbyte.integrations.destination.bigquery.formatter.normalizedPrecision
import io.airbyte.integrations.destination.bigquery.formatter.normalizedScale
import java.math.BigDecimal
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class BigDecimalUtilTest {
    @Test
    fun testMaxForRange() {
        assertEquals(
            BigDecimal("999.99"),
            // 5 significant figures; 2 decimal points
            BigDecimalUtil.maxForRange(precision = 5, scale = 2),
        )
    }

    @Test
    fun testNormalizedPrecision() {
        assertEquals(6, BigDecimal("123.456").normalizedPrecision())
        assertEquals(3, BigDecimal("123").normalizedPrecision())
        // precision() = 3 (b/c BigDecimal represents this as 123 * 1000)
        assertEquals(6, BigDecimal("1.23E5").normalizedPrecision())
    }

    @Test
    fun testNormalizedScale() {
        assertEquals(3, BigDecimal("123.456").normalizedScale())
        assertEquals(0, BigDecimal("123").normalizedScale())
        // scale = -3 (b/c BigDecimal represents this as 123 * 1000)
        assertEquals(0, BigDecimal("1.23E5").normalizedScale())
    }
}
