/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.util

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JsonsTest {

    /**
     * Reproducer for oncall#12768: a single CDC row contained a column value larger than the
     * Jackson default 20 MiB cap, causing Jackson to throw StreamConstraintsException. The bulk CDK
     * mapper must accept arbitrarily large string values.
     */
    @Test
    fun deserializeAcceptsStringValueLargerThan100MiB() {
        val sizeBytes = 110 * 1024 * 1024 // 110 MiB
        val bigValue = CharArray(sizeBytes) { 'x' }
        val json = StringBuilder(sizeBytes + 32)
        json.append("{\"field\":\"")
        json.append(bigValue)
        json.append("\"}")
        val node = Jsons.readTree(json.toString())
        Assertions.assertEquals(sizeBytes, node["field"].asText().length)
    }

    @Test
    fun maxStringLengthIsUnbounded() {
        Assertions.assertEquals(
            Int.MAX_VALUE,
            Jsons.factory.streamReadConstraints().maxStringLength,
        )
    }
}
