package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecord

interface DataMunger {
    fun transform(msg: DestinationRecord): Map<String, AirbyteValue>
}
