/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.pipeline

interface DataFlowStage {
    suspend fun apply(input: DataFlowStageIO): DataFlowStageIO
}
