/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import jakarta.inject.Named
import jakarta.inject.Singleton

@Named("flush")
@Singleton
class FlushStage : DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val agg = input.aggregate!!
        agg.flush()
        return input
    }
}
