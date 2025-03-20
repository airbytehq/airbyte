/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.state.DestinationFailure
import io.airbyte.cdk.load.state.DestinationSuccess
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TaskLauncher
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Secondary
import java.io.InputStream
import javax.inject.Singleton
import kotlinx.coroutines.runBlocking

/**
 * Allows the write operation to be overridden completely. This is not intended for developing
 * production connectors, but for making non-release test tags. (For example, performance
 * experiments to test in the cloud.)
 */
interface WriteOpOverride : Task

/**
 * Write operation. Executed by the core framework when the operation is "write". Launches the core
 * services and awaits completion.
 */
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class WriteOperation(
    private val taskLauncher: TaskLauncher,
    private val syncManager: SyncManager,
    private val writeOpOverride: WriteOpOverride? = null
) : Operation {
    val log = KotlinLogging.logger {}

    override fun execute() = runBlocking {
        if (writeOpOverride != null) {
            val now = System.currentTimeMillis()
            log.info { "Running override task" }
            writeOpOverride.execute()
            log.info { "Write operation override took ${System.currentTimeMillis() - now} ms" }
            throw IllegalStateException(
                "WriteOpOverride is not intended for production use. This exception exists to prevent accidental release. To create a test tag, comment out this exception and uncomment `return @runBlocking` below."
            )
            // return@runBlocking
        }

        taskLauncher.run()

        when (val result = syncManager.awaitDestinationResult()) {
            is DestinationSuccess -> {
                if (!syncManager.allStreamsComplete()) {
                    log.info {
                        "Destination completed successfully but some streams were incomplete. Throwing to exit non-zero..."
                    }
                    throw StreamsIncompleteException()
                }
                log.info { "Destination completed successfully and all streams were complete." }
            }
            is DestinationFailure -> {
                log.info { "Destination failed with stream results ${result.streamResults}" }
                throw result.cause
            }
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
