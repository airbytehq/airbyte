/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.SpilledRawMessagesLocalFile
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Primary
@Requires(env = ["MockTaskLauncher"])
class MockTaskLauncher(override val taskRunner: TaskRunner) : DestinationTaskLauncher {
    val spilledFiles = mutableListOf<BatchEnvelope<SpilledRawMessagesLocalFile>>()
    val batchEnvelopes = mutableListOf<BatchEnvelope<*>>()

    override suspend fun handleSetupComplete() {
        throw NotImplementedError()
    }

    override suspend fun handleStreamStarted(stream: DestinationStream) {
        throw NotImplementedError()
    }

    override suspend fun handleNewSpilledFile(
        stream: DestinationStream,
        wrapped: BatchEnvelope<SpilledRawMessagesLocalFile>
    ) {
        spilledFiles.add(wrapped)
    }

    override suspend fun handleNewBatch(stream: DestinationStream, wrapped: BatchEnvelope<*>) {
        batchEnvelopes.add(wrapped)
    }

    override suspend fun handleStreamClosed(stream: DestinationStream) {
        throw NotImplementedError()
    }

    override suspend fun handleTeardownComplete() {
        throw NotImplementedError()
    }

    override suspend fun start() {
        throw NotImplementedError()
    }
}
