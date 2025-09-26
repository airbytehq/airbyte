package io.airbyte.cdk.load.writer.rejected

import io.airbyte.cdk.load.discoverer.operation.extract
import io.airbyte.cdk.load.discoverer.operation.extractArray
import io.airbyte.cdk.load.http.InterpolableResponse
import io.airbyte.cdk.load.interpolation.BooleanInterpolator
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.dlq.toDlqRecord

class BatchIndexRejectedRecordsBuilder(
    private val condition: String,
    private val rejectionField: List<String>,
    private val indexField: List<String>,
    private val fieldsToReport: List<List<String>>) : RejectedRecordsBuilder
{
    private val rawRecords = mutableListOf<DestinationRecordRaw>()
    private val conditionInterpolator = BooleanInterpolator()

    override fun accumulate(record: DestinationRecordRaw) {
        rawRecords.add(record)
    }

    override fun getRejectedRecords(response: InterpolableResponse): List<DestinationRecordRaw> {
        val context = response.getContext()
        if (conditionInterpolator.interpolate(condition, mapOf("response" to context))) {
            return response.body.extractArray(rejectionField).map { rejection ->
                rawRecords[rejection.extract(indexField).asInt()].toDlqRecord(
                    fieldsToReport.associate { field -> generateRejectedRecordKey(field) to rejection.extract(field) }
                )
            }
        }
        return emptyList()
    }

    private fun generateRejectedRecordKey(field: List<String>): String {
        return "rejected_${field.joinToString("-")}"
    }
}
