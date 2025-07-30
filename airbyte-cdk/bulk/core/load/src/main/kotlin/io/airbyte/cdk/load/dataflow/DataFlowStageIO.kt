package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.message.DestinationRecord

data class DataFlowStageIO(
    var skip: Boolean,
    var rec: DestinationRecord?,
    var munged: Map<String, AirbyteValue>?,
    var aggregate: Aggregate?,
    var stateHist: StateHistogram?,
)
