/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.Test

class PipelineStartHandlerTest {
    @Test
    fun `run`() {
        // Given
        val reconciler = mockk<StateReconciler>(relaxed = true)
        val pipelineStartHandler = PipelineStartHandler(reconciler)

        // When
        pipelineStartHandler.run()

        // Then
        verify(exactly = 1) { reconciler.run() }
    }
}
