package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.DestinationRecordRaw

data class DataFlowStageIO(
    var skip: Boolean,
    var raw: DestinationRecordRaw?,
    var munged: RecordDTO?,
    var aggregate: Aggregate?,
    var stateHist: StateHistogram?,
)
