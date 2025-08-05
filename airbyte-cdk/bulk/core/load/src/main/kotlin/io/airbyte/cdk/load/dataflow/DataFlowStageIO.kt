/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.dataflow.state.StateKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.DestinationRecordRaw

data class DataFlowStageIO(
  var raw: DestinationRecordRaw? = null,
  var stateKey: StateKey? = null,
  var munged: RecordDTO? = null,
  var aggregate: Aggregate? = null,
  var stateHistogram: StateHistogram? = null,
)
