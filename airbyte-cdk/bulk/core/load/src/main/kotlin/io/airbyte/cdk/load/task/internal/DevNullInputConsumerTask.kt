/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.DestinationFileStreamComplete
import io.airbyte.cdk.load.message.DestinationFileStreamIncomplete
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.DestinationRecordStreamIncomplete
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.Undefined
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.protocol.models.v0.AirbyteMessage
import java.util.function.Consumer

class DevNullInputConsumerTask(
    private val inputFlow: ReservingDeserializingInputFlow,
    private val outputConsumer: Consumer<AirbyteMessage>,
    private val syncManager: SyncManager,
    private val catalog: DestinationCatalog,
) : InputConsumerTask {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        try {
            inputFlow.collect { (_, message) ->
                when (message.value) {
                    is GlobalCheckpoint,
                    is StreamCheckpoint -> outputConsumer.accept(message.value.asProtocolMessage())
                    is DestinationFile,
                    is DestinationFileStreamComplete,
                    is DestinationFileStreamIncomplete ->
                        throw NotImplementedError(
                            "DevNullInputConsumerTask does not support DestinationFile"
                        )
                    is DestinationRecord,
                    is DestinationRecordStreamComplete,
                    is DestinationRecordStreamIncomplete,
                    Undefined -> {
                        /* dev-null */
                    }
                }
                message.release()
            }
        } finally {
            catalog.streams.forEach {
                val streamManager = syncManager.getStreamManager(it.descriptor)
                streamManager.markEndOfStream(true)
                streamManager.markProcessingSucceeded()
            }
            syncManager.markDestinationSucceeded()
        }
    }
}
