/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats.socket

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.Histogram
import io.airbyte.cdk.load.dataflow.state.stats.EmissionStats
import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** Stores counts and bytes per stream. For stats emitter. */
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
@Singleton
class EmittedStatsStoreImpl(
    private val catalog: DestinationCatalog,
) : EmittedStatsStore {
    private val readCounts = Histogram<DestinationStream.Descriptor>()

    private val readBytes = Histogram<DestinationStream.Descriptor>()

    override fun increment(
        s: DestinationStream.Descriptor,
        count: Long,
        bytes: Long,
    ) {
        readCounts.increment(s, count.toDouble())
        readBytes.increment(s, bytes.toDouble())
    }

    override fun getStats(): List<AirbyteMessage> =
        catalog.streams
            .map { Pair(it.unmappedDescriptor, get(it.unmappedDescriptor)) }
            .filter { it.second.count > 0 }
            .map { buildMessage(it.first, it.second) }

    @VisibleForTesting
    internal fun get(s: DestinationStream.Descriptor) =
        EmissionStats(
            count = readCounts.get(s)?.toLong() ?: 0,
            bytes = readBytes.get(s)?.toLong() ?: 0,
        )

    @VisibleForTesting
    internal fun buildMessage(
        s: DestinationStream.Descriptor,
        stats: EmissionStats,
    ): AirbyteMessage =
        AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withNamespace(s.namespace)
                    .withStream(s.name)
                    .withData(EMPTY_JSON)
                    .withAdditionalProperty(OutputConsumer.IS_DUMMY_STATS_MESSAGE, true)
                    .withAdditionalProperty(DEST_EMITTED_RECORDS_COUNT, stats.count)
                    .withAdditionalProperty(DEST_EMITTED_BYTES_COUNT, stats.bytes),
            )

    companion object {
        private const val DEST_EMITTED_RECORDS_COUNT = "emittedRecordsCount"
        private const val DEST_EMITTED_BYTES_COUNT = "emittedBytesCount"
        private val EMPTY_JSON = Jsons.emptyObject()
    }
}
