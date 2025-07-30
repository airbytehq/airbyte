package io.airbyte.cdk.load.lifecycle.steps

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.message.DestinationRecordRaw

interface RecordMungingStep {
    fun transformForDest(record: DestinationRecordRaw): Map<String, AirbyteValue>
}
