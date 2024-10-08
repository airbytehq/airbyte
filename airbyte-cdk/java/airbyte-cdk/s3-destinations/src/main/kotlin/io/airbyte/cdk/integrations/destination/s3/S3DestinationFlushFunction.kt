/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3

import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.record_buffer.BufferingStrategy
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.stream.Stream

class S3DestinationFlushFunction(
    override val optimalBatchSizeBytes: Long,
    private val strategyProvider: () -> BufferingStrategy,
    private val generationAndSyncIds: Map<StreamDescriptor, Pair<Long, Long>> = emptyMap()
) : DestinationFlushFunction {

    override fun flush(streamDescriptor: StreamDescriptor, stream: Stream<PartialAirbyteMessage>) {
        val nameAndNamespace =
            AirbyteStreamNameNamespacePair(streamDescriptor.name, streamDescriptor.namespace)
        strategyProvider().use { strategy ->
            for (partialMessage in stream) {
                val partialRecord = partialMessage.record!!
                val data =
                /**
                 * This should always be null, but if something changes upstream to trigger a clone
                 * of the record, then `null` becomes `JsonNull` and `data == null` goes from `true`
                 * to `false`
                 */
                if (partialRecord.data == null || partialRecord.data!!.isNull) {
                        Jsons.deserialize(partialMessage.serialized)
                    } else {
                        partialRecord.data
                    }
                val completeRecord =
                    AirbyteRecordMessage()
                        .withEmittedAt(partialRecord.emittedAt)
                        .withMeta(partialRecord.meta ?: AirbyteRecordMessageMeta())
                        .withNamespace(partialRecord.namespace)
                        .withStream(partialRecord.stream!!)
                        .withData(data)
                val completeMessage =
                    AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(completeRecord)
                val (generationId, syncId) = generationAndSyncIds[streamDescriptor] ?: Pair(0L, 0L)
                strategy.addRecord(nameAndNamespace, completeMessage, generationId, syncId)
            }
            strategy.flushSingleStream(nameAndNamespace)
        }
    }
}
