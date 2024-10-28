/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import io.airbyte.cdk.ConnectorUncleanExitException
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.Requires
import java.io.PipedInputStream
import java.io.PipedOutputStream
import java.io.PrintWriter
import java.util.concurrent.Executors
import javax.inject.Singleton
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class NonDockerizedDestination(
    command: String,
    configContents: String?,
    catalog: ConfiguredAirbyteCatalog?,
    vararg featureFlags: FeatureFlag,
) : DestinationProcess {
    private val destinationStdinPipe: PrintWriter
    private val destination: CliRunnable
    private val destinationComplete = CompletableDeferred<Unit>()
    // The destination has a runBlocking inside WriteOperation.
    // This means that normal coroutine cancellation doesn't work.
    // So we start our own thread pool, which we can forcibly kill if needed.
    private val executor = Executors.newSingleThreadExecutor()
    private val coroutineDispatcher = executor.asCoroutineDispatcher()

    init {
        val destinationStdin = PipedInputStream()
        // This could probably be a channel, somehow. But given the current structure,
        // it's easier to just use the pipe stuff.
        destinationStdinPipe =
            // spotbugs requires explicitly specifying the charset,
            // so we also have to specify autoFlush=false (i.e. the default behavior
            // from PrintWriter(outputStream) ).
            // Thanks, spotbugs.
            PrintWriter(PipedOutputStream(destinationStdin), false, Charsets.UTF_8)
        destination =
            CliRunner.destination(
                command,
                configContents = configContents,
                catalog = catalog,
                inputStream = destinationStdin,
                featureFlags = featureFlags,
            )
    }

    override suspend fun run() {
        withContext(coroutineDispatcher) {
                launch {
                    try {
                        destination.run()
                    } catch (e: ConnectorUncleanExitException) {
                        throw DestinationUncleanExitException.of(
                            e.exitCode,
                            destination.results.traces()
                        )
                    }
                    destinationComplete.complete(Unit)
                }
            }
            .invokeOnCompletion { executor.shutdownNow() }
    }

    override fun sendMessage(message: AirbyteMessage) {
        destinationStdinPipe.println(Jsons.serialize(message))
    }

    override fun readMessages(): List<AirbyteMessage> = destination.results.newMessages()

    override suspend fun shutdown() {
        destinationStdinPipe.close()
        destinationComplete.join()
    }

    override fun kill() {
        // In addition to preventing the executor from accepting new tasks,
        // this also sends a Thread.interrupt() to running tasks.
        // Coroutines interpret this as a cancellation.
        executor.shutdownNow()
    }
}

// Notably, not actually a Micronaut factory. We want to inject the actual
// factory into our tests, not a pre-instantiated destination, because we want
// to run multiple destination processes per test.
@Singleton
@Requires(notEnv = [DOCKERIZED_TEST_ENV])
class NonDockerizedDestinationFactory : DestinationProcessFactory() {
    override fun createDestinationProcess(
        command: String,
        configContents: String?,
        catalog: ConfiguredAirbyteCatalog?,
        vararg featureFlags: FeatureFlag,
    ): DestinationProcess {
        // TODO pass test name into the destination process
        return NonDockerizedDestination(command, configContents, catalog, *featureFlags)
    }
}
