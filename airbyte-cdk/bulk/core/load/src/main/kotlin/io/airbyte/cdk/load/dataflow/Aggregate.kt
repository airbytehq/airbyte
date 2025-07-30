package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.dataflow.state.StateHistogram
import io.airbyte.cdk.load.dataflow.transform.RecordDTO

interface Aggregate {
    enum class Status {
        COMPLETE,
        INCOMPLETE,
    }

    fun accept(fields: RecordDTO): Status

    fun getStateHistogram(): StateHistogram

    suspend fun flush() // Maybe we want some sort of generalizable result

    fun size(): Int
}
