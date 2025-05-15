/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.toList

/**
 * Wraps @[StreamLoader.start] and starts the spill-to-disk tasks.
 *
 * TODO: There's no reason to wait on initialization to start spilling to disk.
 */
@Singleton
class OpenStreamTask(
    private val destinationWriter: DestinationWriter,
    private val syncManager: SyncManager,
    private val openStreamQueue: MessageQueue<DestinationStream>
) : Task {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        val results =
            openStreamQueue
                .consume()
                .map { stream ->
                    val streamLoader = destinationWriter.createStreamLoader(stream)
                    val result = runCatching {
                        streamLoader.start()
                        streamLoader
                    }
                    syncManager.registerStartedStreamLoader(
                        stream.descriptor,
                        result
                    ) // throw after registering the failure
                    result
                }
                .toList()
        results.forEach { it.getOrThrow() }
    }
}
