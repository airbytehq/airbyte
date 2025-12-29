/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.PartitionKey

/**
 * Data transfer object containing a transformed record ready for aggregation and loading.
 *
 * This DTO represents a record after it has been processed through the transformation pipeline,
 * with all field mappings and value coercion already applied. It contains the minimal metadata
 * needed for the aggregation and loading phases.
 *
 * @property fields Map of destination column names to their transformed values. All field name
 * transformations and value coercion have been applied at this point. Most relevant field for
 * destination implementations.
 * @property partitionKey Internal CDK field for routing records to aggregates. This is managed by
 * the CDK and should not be used by destination implementations.
 * @property sizeBytes Estimated size of this record in bytes, used by the CDK for memory management
 * and triggering aggregate flushes based on size thresholds.
 * @property emittedAtMs Timestamp when this record was emitted from the source, in milliseconds
 * since epoch. Used by the CDK for tracking data freshness and latency metrics.
 */
data class RecordDTO(
    val fields: Map<String, AirbyteValue>,
    val partitionKey: PartitionKey,
    val sizeBytes: Long,
    val emittedAtMs: Long,
)
