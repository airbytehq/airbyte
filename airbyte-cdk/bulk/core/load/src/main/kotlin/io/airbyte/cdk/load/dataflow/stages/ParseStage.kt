/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.stages

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStage
import io.airbyte.cdk.load.dataflow.pipeline.DataFlowStageIO
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.dataflow.transform.medium.ConversionInput
import io.airbyte.cdk.load.dataflow.transform.medium.JsonConverter
import io.airbyte.cdk.load.dataflow.transform.medium.ProtobufConverter
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import jakarta.inject.Named
import jakarta.inject.Singleton

@Named("parse")
@Singleton
class ParseStage(
    private val jsonConverter: JsonConverter,
    private val protobufConverter: ProtobufConverter
) : DataFlowStage {
    override suspend fun apply(input: DataFlowStageIO): DataFlowStageIO {
        val raw = input.raw!!
        val fields = transform(raw, input.partitionKey!!)
        return input.apply {
            munged =
                RecordDTO(
                    fields = fields,
                    partitionKey = input.partitionKey!!,
                    sizeBytes = raw.serializedSizeBytes,
                    emittedAtMs = raw.rawData.emittedAtMs,
                )
        }
    }

    private fun transform(
        msg: DestinationRecordRaw,
        partitionKey: PartitionKey
    ): Map<String, AirbyteValue> {
        val input = ConversionInput(msg = msg, partitionKey = partitionKey)
        return when (msg.rawData) {
            is DestinationRecordProtobufSource -> protobufConverter.convert(input)
            else -> jsonConverter.convert(input)
        }
    }
}
