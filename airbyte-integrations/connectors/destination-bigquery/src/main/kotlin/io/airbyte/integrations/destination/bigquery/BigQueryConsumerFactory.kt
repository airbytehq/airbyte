/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.operation.SyncOperation
import io.airbyte.integrations.base.destination.operation.DefaultFlush
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.*
import java.util.function.Consumer

object BigQueryConsumerFactory {

    fun createStagingConsumer(
        outputRecordCollector: Consumer<AirbyteMessage>,
        syncOperation: SyncOperation,
        catalog: ConfiguredAirbyteCatalog,
        defaultNamespace: String
    ): AsyncStreamConsumer {
        // values here are resurrected from some old code.
        // TODO: Find why max memory ratio is 0.4 capped
        return AsyncStreamConsumer(
            outputRecordCollector = outputRecordCollector,
            onStart = {},
            onClose = { _, streamSyncSummaries ->
                syncOperation.finalizeStreams(streamSyncSummaries)
            },
            onFlush = DefaultFlush(200 * 1024 * 1024, syncOperation),
            catalog = catalog,
            bufferManager =
                BufferManager(
                    (Runtime.getRuntime().maxMemory() * 0.4).toLong(),
                ),
            defaultNamespace = Optional.of(defaultNamespace),
        )
    }

    fun createDirectUploadConsumer(
        outputRecordCollector: Consumer<AirbyteMessage>,
        syncOperation: SyncOperation,
        catalog: ConfiguredAirbyteCatalog,
        defaultNamespace: String
    ): AsyncStreamConsumer {

        // TODO: Why is Standard consumer operating at memory ratio of 0.5
        //  and Max 2 threads and some weird 20% max memory as the default flush size.
        return AsyncStreamConsumer(
            outputRecordCollector = outputRecordCollector,
            onStart = {},
            onClose = { _, streamSyncSummaries ->
                syncOperation.finalizeStreams(streamSyncSummaries)
            },
            onFlush =
                DefaultFlush((Runtime.getRuntime().maxMemory() * 0.2).toLong(), syncOperation),
            catalog = catalog,
            bufferManager =
                BufferManager(
                    (Runtime.getRuntime().maxMemory() * 0.5).toLong(),
                ),
            defaultNamespace = Optional.of(defaultNamespace),
        )
    }
}
