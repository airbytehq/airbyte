/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class AirbyteFileUtilsTest {
    @ParameterizedTest
    @CsvSource(
        value =
            [
                "500,500 bytes",
                "2000,1.95 KB",
                "3072000,2.93 MB",
                "2872000000,2.67 GB",
                "2000000000000,1.82 TB"
            ]
    )
    internal fun `test converting a byte count to a display string`(
        sizeInBytes: String,
        expected: String,
    ) {
        assertEquals(expected, AirbyteFileUtils().byteCountToDisplaySize(sizeInBytes.toLong()))
    }
}
