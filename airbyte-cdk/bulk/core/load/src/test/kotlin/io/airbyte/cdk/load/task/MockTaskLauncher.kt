/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.BatchEnvelope
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Primary
@Requires(env = ["MockTaskLauncher"])
class MockTaskLauncher : DestinationTaskLauncher {
    val batchEnvelopes = mutableListOf<BatchEnvelope<*>>()

    override suspend fun handleSetupComplete() {
        throw NotImplementedError()
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

    override suspend fun handleTeardownComplete(success: Boolean) {
        throw NotImplementedError()
    }

    override suspend fun handleException(e: Exception) {
        TODO("Not yet implemented")
    }

    override suspend fun handleFailStreamComplete(
        stream: DestinationStream.Descriptor,
        e: Exception
    ) {
        TODO("Not yet implemented")
    }

    override suspend fun run() {
        throw NotImplementedError()
    }
}
