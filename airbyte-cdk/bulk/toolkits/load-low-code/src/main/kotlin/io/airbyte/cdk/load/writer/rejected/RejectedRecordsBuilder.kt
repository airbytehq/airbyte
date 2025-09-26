package io.airbyte.cdk.load.writer.rejected

import io.airbyte.cdk.load.http.InterpolableResponse
import io.airbyte.cdk.load.message.DestinationRecordRaw

interface RejectedRecordsBuilder {
    /**
     * Indicates records that are added to the batch. This assumes that the records are accumulated
     * in the same order they will be presented in the request.
     */
    fun accumulate(record: DestinationRecordRaw)
    fun getRejectedRecords(response: InterpolableResponse): List<DestinationRecordRaw>
}
