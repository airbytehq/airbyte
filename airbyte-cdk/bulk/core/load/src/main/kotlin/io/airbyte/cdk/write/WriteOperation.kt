/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.write

import io.airbyte.cdk.Operation
import io.airbyte.cdk.task.TaskLauncher
import io.airbyte.cdk.task.TaskRunner
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import java.io.InputStream
import javax.inject.Singleton
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

/**
 * Write operation. Executed by the core framework when the operation is "write". Launches the core
 * services and awaits completion.
 */
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperation(
    private val inputConsumer: InputConsumer<*>,
    private val taskLauncher: TaskLauncher,
    private val taskRunner: TaskRunner,
) : Operation {
    val log = KotlinLogging.logger {}

    override fun execute() {
        runBlocking {
            /**
             * Start the consumer, runner and launcher in their own scope. Failures in any will
             * cancel the entire scope.
             *
             * If the scope fails, restart the task runner and invoke the launcher's exception
             * handler.
             */
            try {
                coroutineScope {
                    launch { inputConsumer.run() } // read messages
                    launch { taskRunner.start() } // run enqueued tasks
                    launch { taskLauncher.start() } // start the task workflow
                }
            } catch (t: Throwable) {
                // Restart the task runner so the handler can launch tasks.
                launch { taskRunner.restart() }
                // TODO: wrap any exceptions thrown here
                //  in the fancy exception mapper.
                taskLauncher.handleException(t)
            }
        }
    }
}

/** Override to provide a custom input stream. */
@Factory
class InputStreamFactory {
    @Singleton
    @Secondary
    @Requires(property = Operation.PROPERTY, value = "write")
    fun make(): InputStream {
        return System.`in`
    }
}
