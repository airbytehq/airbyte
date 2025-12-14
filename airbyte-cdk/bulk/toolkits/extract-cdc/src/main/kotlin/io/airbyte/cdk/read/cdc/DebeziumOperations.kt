/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

/** Stateless connector-specific Debezium operations. */
@Deprecated("Implement the two interfaces separately")
interface DebeziumOperations<T : PartiallyOrdered<T>> :
    CdcPartitionsCreatorDebeziumOperations<T>, CdcPartitionReaderDebeziumOperations<T>
