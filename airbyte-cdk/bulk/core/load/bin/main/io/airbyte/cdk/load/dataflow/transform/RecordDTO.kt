/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.PartitionKey

/** Internal DTO for passing of record data with minimal metadata. */
data class RecordDTO(
    val fields: Map<String, AirbyteValue>,
    val partitionKey: PartitionKey,
    val sizeBytes: Long,
    val emittedAtMs: Long,
)
