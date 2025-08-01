package io.airbyte.cdk.load.dataflow.aggregate

import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO

interface Aggregate {
    enum class Status {
        COMPLETE,
        INCOMPLETE,
    }

    fun accept(fields: RecordDTO): Status

    suspend fun flush() // Maybe we want some sort of generalizable result

    fun getStateHistogram(): StateHistogram

    fun size(): Int
}

interface AggregateFactory {
    fun create(key: StoreKey): Aggregate
}
