/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

import io.airbyte.cdk.load.dataflow.transform.RecordDTO

/**
 * Represents a batch or aggregation of records to be loaded via bulk operations.
 *
 * Implementations of this interface accumulate records into a batch that will be efficiently loaded
 * into the destination using bulk operations. The CDK automatically handles when to trigger flush
 * based on [AggregatePublishingConfig] settings.
 */
interface Aggregate {

    /**
     * Accepts a record to be added to this aggregate.
     *
     * This method adds the provided record to the current batch and should perform any final
     * per-record processing needed. Note that field and value transformations should be handled
     * upstream before records reach this point (e.g., by the [ValueCoercer] during the
     * transformation phase). The CDK automatically manages when aggregates should be flushed based
     * on configured thresholds (see [AggregatePublishingConfig]).
     *
     * @param record The record to add to this aggregate
     */
    fun accept(record: RecordDTO)

    /**
     * Finalizes this aggregate and loads it into the destination.
     *
     * This method is called by the CDK when the aggregate is ready to be persisted. Implementations
     * should perform the actual bulk load operation to write all accumulated records to the
     * destination.
     */
    suspend fun flush()
}

/**
 * Factory interface for creating [Aggregate] instances.
 *
 * This factory pattern allows for different aggregation strategies to be instantiated based on the
 * provided store key, enabling flexible configuration of the aggregation behavior per data stream
 * or destination.
 */
interface AggregateFactory {
    /**
     * Creates a new [Aggregate] instance for the specified store key.
     *
     * @param key The store key that identifies the target for aggregation
     * @return A new [Aggregate] instance configured for the given key
     */
    fun create(key: StoreKey): Aggregate
}
