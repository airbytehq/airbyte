/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

interface DataFlowStage {
    suspend fun apply(input: DataFlowStageIO): DataFlowStageIO
}
