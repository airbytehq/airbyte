/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.state.StateReconciler
import io.mockk.Runs
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.just
import io.mockk.verify
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class PipelineStartHandlerTest {

    @MockK private lateinit var reconciler: StateReconciler

    private lateinit var pipelineStartHandler: PipelineStartHandler

    @BeforeEach
    fun setUp() {
        pipelineStartHandler = PipelineStartHandler(reconciler)
    }

    @Test
    fun `run should call reconciler run method`() {
        // Given

        every { reconciler.run(any()) } just Runs

        // When
        pipelineStartHandler.run()

        // Then
        verify(exactly = 1) { reconciler.run(any()) }
    }
}
