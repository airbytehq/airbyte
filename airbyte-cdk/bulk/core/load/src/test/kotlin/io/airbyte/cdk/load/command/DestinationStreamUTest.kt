/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.mockk.every
import io.mockk.impl.annotations.MockK
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

class DestinationStreamUTest {
    @MockK(relaxed = true) private lateinit var stream: DestinationStream

    @Test
    fun `test should not truncate incremental append syncs`() {
        every { stream.importType } returns Append
        every { stream.minimumGenerationId } returns 1
        every { stream.generationId } returns 2
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }

    @Test
    fun `test should not truncate overwrite append`() {
        every { stream.importType } returns Overwrite
        every { stream.minimumGenerationId } returns 0
        every { stream.generationId } returns 0
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }

    @Test
    fun `test should truncate overwrite`() {
        every { stream.importType } returns Overwrite
        every { stream.minimumGenerationId } returns 1
        every { stream.generationId } returns 1
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }
}
