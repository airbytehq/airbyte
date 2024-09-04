/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.write

import io.airbyte.cdk.Operation
import io.airbyte.cdk.message.DestinationMessage
import io.airbyte.cdk.task.TaskLauncher
import io.airbyte.cdk.task.TaskRunner
import io.micronaut.context.annotation.Requires
import javax.inject.Singleton
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

/**
 * Write operation. Executed by the core framework when the operation is "write". Launches the core
 * services and awaits completion.
 */
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperation(
    private val inputConsumer: InputConsumer<DestinationMessage>,
    private val taskLauncher: TaskLauncher,
    private val taskRunner: TaskRunner
) : Operation {
    override fun execute() {
        runBlocking {
            launch { inputConsumer.run() }

            launch { taskLauncher.start() }

            launch { taskRunner.run() }
        }
    }
}
