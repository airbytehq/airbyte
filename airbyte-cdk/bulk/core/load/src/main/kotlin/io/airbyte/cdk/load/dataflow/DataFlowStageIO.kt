package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.DestinationRecordRaw

data class DataFlowStageIO(
  var skip: Boolean = false,
  var raw: DestinationRecordRaw? = null,
  var munged: RecordDTO? = null,
  var aggregate: Aggregate? = null,
  var stateHist: StateHistogram? = null,
)
