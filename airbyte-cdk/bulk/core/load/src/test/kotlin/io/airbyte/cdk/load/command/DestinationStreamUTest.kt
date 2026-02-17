/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

class DestinationStreamUTest {
    @MockK(relaxed = true) private lateinit var stream: DestinationStream

    @Test
    fun `test should not truncate incremental append syncs`() {
        val tableSchema = mockk<StreamTableSchema> { every { importType } returns Append }
        every { stream.tableSchema } returns tableSchema
        every { stream.minimumGenerationId } returns 1
        every { stream.generationId } returns 2
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }

    @Test
    fun `test should not truncate overwrite append`() {
        val tableSchema = mockk<StreamTableSchema> { every { importType } returns Overwrite }
        every { stream.tableSchema } returns tableSchema
        every { stream.minimumGenerationId } returns 0
        every { stream.generationId } returns 0
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }

    @Test
    fun `test should truncate overwrite`() {
        val tableSchema = mockk<StreamTableSchema> { every { importType } returns Overwrite }
        every { stream.tableSchema } returns tableSchema
        every { stream.minimumGenerationId } returns 1
        every { stream.generationId } returns 1
        assertFalse(stream.shouldBeTruncatedAtEndOfSync())
    }
}
