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
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

/**
 * Consumes DestinationStreams from the openStreamQueue, creates/starts a StreamLoader for each, and
 * registers it with the SyncManager.
 *
 * Duplicate streams across the entire sync are ignored: start() is called at most once per stream
 * descriptor, even with multiple concurrent workers.
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
        val seen = ConcurrentHashMap.newKeySet<DestinationStream.Descriptor>()
        openStreamQueue.consume().collect { stream ->
            val desc = stream.mappedDescriptor

            if (!seen.add(desc)) return@collect

            val result: Result<io.airbyte.cdk.load.write.StreamLoader> = runCatching {
                val loader = destinationWriter.createStreamLoader(stream)
                loader.start()
                loader
            }
            result.getOrThrow()
            syncManager.registerStartedStreamLoader(desc, result)
        }
    }
}
