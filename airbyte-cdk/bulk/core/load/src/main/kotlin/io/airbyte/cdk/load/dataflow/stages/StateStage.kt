/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.DataFlowStage
import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.StateWatermarkStore
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton

@Named("state")
@Singleton
class StateStage(
    val stateStore: StateWatermarkStore,
) : DataFlowStage {
    private val log = KotlinLogging.logger {}

    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        log.info { "state" }
        val stateUpdates = input.aggregate!!.getStateHistogram()

        stateStore.accept(stateUpdates)

        return input
    }
}
