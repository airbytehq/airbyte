/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteFileUtilsTest {
    @Test
    internal fun testByteCountToDisplaySize() {
        Assertions.assertEquals("500 bytes", AirbyteFileUtils.byteCountToDisplaySize(500L))
        Assertions.assertEquals("1.95 KB", AirbyteFileUtils.byteCountToDisplaySize(2000L))
        Assertions.assertEquals("2.93 MB", AirbyteFileUtils.byteCountToDisplaySize(3072000L))
        Assertions.assertEquals("2.67 GB", AirbyteFileUtils.byteCountToDisplaySize(2872000000L))
        Assertions.assertEquals("1.82 TB", AirbyteFileUtils.byteCountToDisplaySize(2000000000000L))
    }
}
