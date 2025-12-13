/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import io.mockk.mockk
import io.mockk.verify
import java.io.InputStream
import org.junit.jupiter.api.Test

class ConnectorInputStreamsTest {
    @Test
    fun `closeAll should close all input streams`() {
        // Given
        val stream1 = mockk<InputStream>(relaxed = true)
        val stream2 = mockk<InputStream>(relaxed = true)
        val stream3 = mockk<InputStream>(relaxed = true)
        val streams = listOf(stream1, stream2, stream3)
        val connectorInputStreams = ConnectorInputStreams(streams)

        // When
        connectorInputStreams.closeAll()

        // Then
        verify(exactly = 1) { stream1.close() }
        verify(exactly = 1) { stream2.close() }
        verify(exactly = 1) { stream3.close() }
    }
}
