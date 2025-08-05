package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.StateKey

data class RecordDTO(
    val fields: Map<String, AirbyteValue>,
    val stateKey: StateKey,
    val sizeBytes: Long,
    val emittedAtMs: Long,
)
