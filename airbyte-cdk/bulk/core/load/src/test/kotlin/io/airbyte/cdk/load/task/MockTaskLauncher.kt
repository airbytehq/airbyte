/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.task.internal.SpilledRawMessagesLocalFile
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Primary
@Requires(env = ["MockTaskLauncher"])
class MockTaskLauncher : DestinationTaskLauncher {
    val spilledFiles = mutableListOf<SpilledRawMessagesLocalFile>()
    val batchEnvelopes = mutableListOf<BatchEnvelope<*>>()

    override suspend fun handleSetupComplete() {
        throw NotImplementedError()
    }

    override suspend fun handleStreamStarted(stream: DestinationStream.Descriptor) {
        throw NotImplementedError()
    }

    override suspend fun handleNewSpilledFile(
        stream: DestinationStream.Descriptor,
        file: SpilledRawMessagesLocalFile
    ) {
        spilledFiles.add(file)
    }

    override suspend fun handleNewBatch(
        stream: DestinationStream.Descriptor,
        wrapped: BatchEnvelope<*>
    ) {
        batchEnvelopes.add(wrapped)
    }

    override suspend fun handleStreamClosed(stream: DestinationStream.Descriptor) {
        throw NotImplementedError()
    }

    override suspend fun handleTeardownComplete() {
        throw NotImplementedError()
    }

    override suspend fun handleFile(stream: DestinationStream.Descriptor, file: DestinationFile) {
        throw NotImplementedError()
    }

    override suspend fun run() {
        throw NotImplementedError()
    }
}
