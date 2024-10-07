/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.write

import io.airbyte.cdk.Operation
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.state.SyncFailure
import io.airbyte.cdk.state.SyncManager
import io.airbyte.cdk.state.SyncSuccess
import io.airbyte.cdk.task.TaskLauncher
import io.airbyte.cdk.task.TaskRunner
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import java.io.InputStream
import javax.inject.Singleton
import kotlin.system.exitProcess
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

/**
 * Write operation. Executed by the core framework when the operation is "write". Launches the core
 * services and awaits completion.
 */
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperation(
    private val taskLauncher: TaskLauncher,
    private val taskRunner: TaskRunner,
    private val syncManager: SyncManager,
    private val exceptionHandler: ExceptionHandler,
    private val outputConsumer: OutputConsumer
) : Operation {
    val log = KotlinLogging.logger {}

    override fun execute() {
        runCatching {
                runBlocking {
                    launch { taskLauncher.start() }

                    launch { taskRunner.run() }

                    when (val result = syncManager.awaitSyncResult()) {
                        is SyncSuccess -> exitProcess(0)
                        is SyncFailure -> {
                            log.error { "Caught exception during sync: ${result.syncFailure}" }
                            val errorMessage = exceptionHandler.handle(result.syncFailure)
                            outputConsumer.accept(errorMessage)
                            exitProcess(1)
                        }
                    }
                }
            }
            .onFailure {
                log.error { "Uncaught exception during sync: $it" }
                val errorMessage = exceptionHandler.handle(it)
                outputConsumer.accept(errorMessage)
                exitProcess(1)
            }
    }
}

/** Override to provide a custom input stream. */
@Factory
class InputStreamProvider {
    @Singleton
    @Secondary
    @Requires(property = Operation.PROPERTY, value = "write")
    fun make(): InputStream {
        return System.`in`
    }
}
