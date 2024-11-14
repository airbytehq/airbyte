/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.ImplementorScope
import io.airbyte.cdk.load.task.StreamLevel
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton

interface ProcessFileTask : StreamLevel, ImplementorScope

class DefaultProcessFileTask(
    override val streamDescriptor: DestinationStream.Descriptor,
    private val taskLauncher: DestinationTaskLauncher,
    private val syncManager: SyncManager,
    private val file: DestinationFile
) : ProcessFileTask {
    val log = KotlinLogging.logger {}

    override suspend fun execute() {
        val streamLoader = syncManager.getOrAwaitStreamLoader(streamDescriptor)

        val batch = streamLoader.processFile(file)

        val wrapped = BatchEnvelope(batch)
        taskLauncher.handleNewBatch(streamDescriptor, wrapped)
    }
}

interface ProcessFileTaskFactory {
    fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream.Descriptor,
        file: DestinationFile,
    ): ProcessFileTask
}

@Singleton
@Secondary
class DefaultFileRecordsTaskFactory(
    private val syncManager: SyncManager,
) : ProcessFileTaskFactory {
    override fun make(
        taskLauncher: DestinationTaskLauncher,
        stream: DestinationStream.Descriptor,
        file: DestinationFile,
    ): ProcessFileTask {
        return DefaultProcessFileTask(stream, taskLauncher, syncManager, file)
    }
}
