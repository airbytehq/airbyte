package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.StateHistogram

interface Aggregate {
    enum class Status {
        COMPLETE,
        INCOMPLETE,
    }

    fun accept(fields: Map<String, AirbyteValue>): Status

    fun getStateHistogram(): StateHistogram

    suspend fun flush() // Maybe we want some sort of generalizable result

    fun size(): Int
}
