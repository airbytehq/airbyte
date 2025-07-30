package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.dataflow.DataFlowStage
import io.airbyte.cdk.load.dataflow.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.DataMunger
import io.airbyte.cdk.load.dataflow.transform.RecordDTO

class ParseStage(
    val munger: DataMunger,
): DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val raw = input.raw!!
        val fields = munger.transform(raw)
        return input.apply {
            munged = RecordDTO(
                fields = fields,
                stateId = raw.checkpointId!!.value,
                sizeBytes = raw.serializedSizeBytes,
            )
        }
    }
}
