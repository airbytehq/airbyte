/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.dataflow.transform.RecordMunger
import jakarta.inject.Named
import jakarta.inject.Singleton

@Named("parse")
@Singleton
class ParseStage(
    private val munger: RecordMunger,
) : DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val partitionKey = input.partitionKey!!
        val raw = input.raw!!
        // pass this key down somehow, or pull the validation up so you can associate it to the counters
        val fields = munger.transformForDest(raw, partitionKey)

        return input.apply {
            munged =
                RecordDTO(
                    fields = fields,
                    partitionKey = partitionKey,
                    sizeBytes = raw.serializedSizeBytes,
                    emittedAtMs = raw.rawData.emittedAtMs,
                )
        }
    }
}
