/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.aggregate

import io.airbyte.cdk.load.dataflow.transform.RecordDTO

interface Aggregate {

    fun accept(record: RecordDTO)

    suspend fun flush()
}

interface AggregateFactory {
    fun create(key: StoreKey): Aggregate
}
