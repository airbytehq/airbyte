package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordRaw

interface DataMunger {
    fun transform(msg: DestinationRecordRaw): Map<String, AirbyteValue>
}
