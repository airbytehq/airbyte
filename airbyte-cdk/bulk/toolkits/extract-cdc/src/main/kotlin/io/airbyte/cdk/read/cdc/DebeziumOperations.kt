/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

/** Stateless connector-specific Debezium operations. */
@Deprecated("Implement the two interfaces separately")
interface DebeziumOperations<T : Comparable<T>> :
    CdcPartitionsCreatorDebeziumOperations<T>, CdcPartitionReaderDebeziumOperations<T>
