/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.dlq

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class ObjectStorageConfigTest {
    @Test
    fun `normalizePathFormat should not duplicate trailing slash`() {
        assertEquals("my/path/", normalizePathFormat("my/path/"))
    }

    @Test
    fun `normalizePathFormat should uppercase and $ to variables`() {
        assertEquals("my/${'$'}{STREAM_NAME}/", normalizePathFormat("my/{stream_name}/"))
    }

    @Test
    fun `normalizePathFormat should process all variables`() {
        assertEquals(
            "${'$'}{NAMESPACE}/and/${'$'}{STREAM_NAME}/${'$'}{DAY}/",
            normalizePathFormat("{namespace}/and/{stream_name}/{day}/"),
        )
    }
}
