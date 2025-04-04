/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.data.FlowConnector
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.flow.consumeAsFlow
import kotlinx.coroutines.launch

class DirectInputFlow(
    private val catalog: DestinationCatalog,
) : Flow<PipelineEvent<StreamKey, DestinationRecordRaw>>, FlowConnector {
    private val channel = Channel<PipelineEvent<StreamKey, DestinationRecordRaw>>()

    override suspend fun collect(
        collector:
            FlowCollector<
                PipelineEvent<
                    StreamKey,
                    DestinationRecordRaw,
                >,
            >,
    ) {
        channel.consumeAsFlow().collect(collector)
    }

    override fun close() {
        channel.close()
    }

    override fun pipe(message: AirbyteMessage) {
        CoroutineScope(Dispatchers.IO).launch {
            val stream =
                catalog.getStream(
                    namespace = message.record.namespace,
                    name = message.record.stream,
                )
            val streamKey = StreamKey(stream.descriptor)
            val destinationRecordRaw = DestinationRecordRaw(stream, message, "", stream.schema)
            channel.send(PipelineMessage(mutableMapOf(), streamKey, destinationRecordRaw))
        }
    }
}

@Factory
class FlowFactory {
    @Singleton
    fun inputFlows(
        configuration: MySqlSourceConfiguration<*>,
        catalog: DestinationCatalog,
    ): Array<
        Flow<
            PipelineEvent<
                StreamKey,
                DestinationRecordRaw,
            >,
        >,
    > = (0..configuration.numThreads).map { DirectInputFlow(catalog) }.toTypedArray()
}
