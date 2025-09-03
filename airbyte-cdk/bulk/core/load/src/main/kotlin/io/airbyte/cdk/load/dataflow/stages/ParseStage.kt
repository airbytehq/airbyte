/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.transform.DataMunger
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import jakarta.inject.Named
import jakarta.inject.Singleton

@Named("parse")
@Singleton
class ParseStage(
    val munger: DataMunger,
) : DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val raw = input.raw!!
        val fields = munger.transformForDest(raw)

        return input.apply {
            munged =
                RecordDTO(
                    fields = fields,
                    partitionKey = input.partitionKey!!,
                    sizeBytes = raw.serializedSizeBytes,
                    emittedAtMs = raw.rawData.emittedAtMs,
                )
        }
    }
}
