/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.task

import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.message.BatchEnvelope
import io.airbyte.cdk.message.SpooledRawMessagesLocalFile
import io.airbyte.cdk.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Provider
import jakarta.inject.Singleton

/**
 * Governs the task workflow for the entire destination life-cycle.
 *
 * The domain is "decide what to do next given the reported results of the individual task."
 *
 * TODO: Some of that logic still lives in the tasks. Migrate it here.
 */
class DestinationTaskLauncher(
    private val catalog: DestinationCatalog,
    override val taskRunner: TaskRunner,
    private val setupTaskFactory: SetupTaskFactory,
    private val openStreamTaskFactory: OpenStreamTaskFactory,
    private val spillToDiskTaskFactory: SpillToDiskTaskFactory,
    private val processRecordsTaskFactory: ProcessRecordsTaskFactory,
    private val processBatchTaskFactory: ProcessBatchTaskFactory,
    private val closeStreamTaskFactory: CloseStreamTaskFactory,
    private val teardownTaskFactory: TeardownTaskFactory
) : TaskLauncher {
    private val log = KotlinLogging.logger {}

    override suspend fun start() {
        log.info { "Starting startup task" }
        taskRunner.enqueue(setupTaskFactory.make(this))
    }

    suspend fun startOpenStreamTasks() {
        catalog.streams.forEach {
            log.info { "Starting open stream task for $it" }
            taskRunner.enqueue(openStreamTaskFactory.make(this, it))
        }
    }

    suspend fun startSpillToDiskTasks(streamLoader: StreamLoader) {
        log.info { "Starting spill-to-disk task for ${streamLoader.stream}" }
        val task = spillToDiskTaskFactory.make(this, streamLoader)
        taskRunner.enqueue(task)
    }

    suspend fun startProcessRecordsTask(
        streamLoader: StreamLoader,
        fileEnvelope: BatchEnvelope<SpooledRawMessagesLocalFile>
    ) {
        log.info {
            "Starting process records task for ${streamLoader.stream}, file ${fileEnvelope.batch}"
        }
        taskRunner.enqueue(processRecordsTaskFactory.make(this, streamLoader, fileEnvelope))
    }

    suspend fun startProcessBatchTask(streamLoader: StreamLoader, batch: BatchEnvelope<*>) {
        log.info { "Starting process batch task for ${streamLoader.stream}, batch ${batch.batch}" }
        taskRunner.enqueue(processBatchTaskFactory.make(this, streamLoader, batch))
    }

    suspend fun startCloseStreamTasks(streamLoader: StreamLoader) {
        log.info { "Starting close stream task for ${streamLoader.stream}" }
        taskRunner.enqueue(closeStreamTaskFactory.make(this, streamLoader))
    }

    suspend fun startTeardownTask() {
        log.info { "Starting teardown task" }
        taskRunner.enqueue(teardownTaskFactory.make(this))
    }
}

@Factory
class DestinationTaskLauncherFactory(
    private val catalog: DestinationCatalog,
    private val taskRunner: TaskRunner,
    private val setupTaskFactory: SetupTaskFactory,
    private val openStreamTaskFactory: OpenStreamTaskFactory,
    private val spillToDiskTaskFactory: SpillToDiskTaskFactory,
    private val processRecordsTaskFactory: ProcessRecordsTaskFactory,
    private val processBatchTaskFactory: ProcessBatchTaskFactory,
    private val closeStreamTaskFactory: CloseStreamTaskFactory,
    private val teardownTaskFactory: TeardownTaskFactory
) : Provider<DestinationTaskLauncher> {
    @Singleton
    @Secondary
    override fun get(): DestinationTaskLauncher {
        return DestinationTaskLauncher(
            catalog,
            taskRunner,
            setupTaskFactory,
            openStreamTaskFactory,
            spillToDiskTaskFactory,
            processRecordsTaskFactory,
            processBatchTaskFactory,
            closeStreamTaskFactory,
            teardownTaskFactory,
        )
    }
}
