package io.airbyte.cdk.load.lifecycle.operations

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordRaw

abstract class Aggregator {
    enum class AggregationStatus {
        COMPLETE,
        INCOMPLETE,
    }

    /**
     * This method need to be implemented if you want to aggregate non-transformed records.
     */
    fun aggregate(destinationRecordRaw: DestinationRecordRaw): AggregationStatus =
        throw NotImplementedError("This aggregate can't ingest non-transformed records")


    open fun aggregate(destiantionRecord: Map<String, AirbyteValue>): AggregationStatus =
        throw NotImplementedError("This aggregate can't ingest transformed records")

    abstract fun flush(): Boolean
}
