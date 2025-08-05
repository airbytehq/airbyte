/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.StateId

data class RecordDTO(
    val fields: Map<String, AirbyteValue>,
    val stateId: StateId,
    val sizeBytes: Long,
    val emittedAtMs: Long,
)
