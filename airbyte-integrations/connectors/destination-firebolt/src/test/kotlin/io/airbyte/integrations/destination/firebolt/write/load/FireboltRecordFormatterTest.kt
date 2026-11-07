/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringValue
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class FireboltRecordFormatterTest {

    @Test
    fun `formats records in column order and emits empty strings for missing columns`() {
        val formatter = FireboltRecordFormatter(columns = listOf("id", "name", "missing"))

        val record: Map<String, AirbyteValue> =
            mapOf(
                "id" to IntegerValue(BigInteger.valueOf(42)),
                "name" to StringValue("hello"),
            )

        val result = formatter.format(record)

        assertEquals(3, result.size)
        assertEquals("42", result[0].toString())
        assertEquals("hello", result[1].toString())
        assertEquals("", result[2])
    }
}
