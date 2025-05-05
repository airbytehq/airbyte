/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton

/** Wraps @[StreamLoader.processBatch] and handles the resulting batch. */
@Singleton
class ProcessBatchTask(
    private val syncManager: SyncManager,
    @Named("batchQueue") private val batchQueue: MultiProducerChannel<BatchEnvelope<*>>,
) : Task() {
    override val terminalCondition: TerminalCondition = SelfTerminating

    val log = KotlinLogging.logger {}
    override suspend fun execute() {
        batchQueue.consume().collect { batchEnvelope ->
            val streamLoader = syncManager.getOrAwaitStreamLoader(batchEnvelope.streamDescriptor)
            val nextBatch = streamLoader.processBatch(batchEnvelope.batch)
            val nextWrapped = batchEnvelope.withBatch(nextBatch)
            taskLauncher!!.handleNewBatch(nextWrapped.streamDescriptor, nextWrapped)
        }
    }
}
