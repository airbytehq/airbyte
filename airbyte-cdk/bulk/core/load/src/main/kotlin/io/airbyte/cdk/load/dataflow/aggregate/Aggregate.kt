package io.airbyte.cdk.load.dataflow.aggregate

import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO

interface Aggregate {

    fun accept(record: RecordDTO)

    suspend fun flush() // Maybe we want some sort of generalizable result

    fun getStateHistogram(): StateHistogram
}

interface AggregateFactory {
    fun create(key: StoreKey): Aggregate
}
