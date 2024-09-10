/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.state.StreamManager
import io.airbyte.cdk.state.StreamsManager
import io.airbyte.cdk.write.StreamLoader
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import org.apache.mina.util.ConcurrentHashSet

/**
 * Wraps @[StreamLoader.close] and marks the stream as closed in the stream manager. Also starts the
 * teardown task.
 */
class CloseStreamTask(
    private val streamLoader: StreamLoader,
    private val streamManager: StreamManager,
    private val taskLauncher: DestinationTaskLauncher
) : Task {
    companion object {
        val oncePerStream: ConcurrentHashSet<DestinationStream> = ConcurrentHashSet()
    }

    override suspend fun execute() {
        /** Guard against running this more than once per stream */
        if (oncePerStream.contains(streamLoader.stream) || streamManager.streamIsClosed()) {
            return
        }
        oncePerStream.add(streamLoader.stream)
        streamLoader.close()
        streamManager.markClosed()
        /* TODO: just signal to the launcher that the stream is closed
        and let it decide what to do next */
        taskLauncher.startTeardownTask()
    }
}

@Singleton
@Secondary
class CloseStreamTaskFactory(
    private val streamsManager: StreamsManager,
) {
    fun make(taskLauncher: DestinationTaskLauncher, streamLoader: StreamLoader): CloseStreamTask {
        return CloseStreamTask(
            streamLoader,
            streamsManager.getManager(streamLoader.stream),
            taskLauncher
        )
    }
}
