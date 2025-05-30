/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import io.airbyte.cdk.ConnectorUncleanExitException
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.command.EnvVarConstants
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.file.ServerSocketWriterOutputStream
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.NUM_SOCKETS
import io.airbyte.cdk.load.test.util.rotate
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.InputStream
import java.io.PipedInputStream
import java.io.PipedOutputStream
import java.io.PrintWriter
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.junit.jupiter.api.Assertions.assertFalse

private val logger = KotlinLogging.logger {}

class NonDockerizedDestination(
    command: String,
    configContents: String?,
    catalog: ConfiguredAirbyteCatalog?,
    useFileTransfer: Boolean,
    additionalMicronautEnvs: List<String>,
    micronautProperties: Map<Property, String>,
    injectInputStream: Boolean,
    override val dataChannelMedium: DataChannelMedium,
    vararg featureFlags: FeatureFlag,
) : DestinationProcess {
    private val destinationStdinPipes: Array<PrintWriter>
    private val onChannel = AtomicInteger(0)
    private val destination: CliRunnable
    private val destinationComplete = CompletableDeferred<Unit>()
    // The destination has a runBlocking inside WriteOperation.
    // This means that normal coroutine cancellation doesn't work.
    // So we start our own thread pool, which we can forcibly kill if needed.
    private val executor = Executors.newSingleThreadExecutor()
    private val coroutineDispatcher = executor.asCoroutineDispatcher()
    private val file = File("/tmp/test_file")

    init {
        if (useFileTransfer) {
            val fileContentStr = "123"
            file.writeText(fileContentStr)
        }
        var destinationStdin: InputStream? = null

        val additionalMicronautProperties =
            when (dataChannelMedium) {
                DataChannelMedium.STDIO -> {
                    // This could probably be a channel, somehow. But given the current structure,
                    // it's easier to just use the pipe stuff.
                    destinationStdin = PipedInputStream()
                    // spotbugs requires explicitly specifying the charset,
                    // so we also have to specify autoFlush=false (i.e. the default behavior
                    // from PrintWriter(outputStream) ).
                    // Thanks, spotbugs.
                    destinationStdinPipes =
                        arrayOf(
                            PrintWriter(PipedOutputStream(destinationStdin), false, Charsets.UTF_8)
                        )
                    mapOf(
                        EnvVarConstants.DATA_CHANNEL_MEDIUM to DataChannelMedium.STDIO.toString(),
                    )
                }
                DataChannelMedium.SOCKETS -> {
                    val socketWriters =
                        (0 until NUM_SOCKETS).map {
                            val socketFile = File.createTempFile("ab_socket_${it}_", ".socket")
                            socketFile.delete()
                            ServerSocketWriterOutputStream(socketFile.path.toString())
                        }
                    destinationStdinPipes = socketWriters.map { PrintWriter(it) }.toTypedArray()
                    mapOf(
                        EnvVarConstants.DATA_CHANNEL_MEDIUM to DataChannelMedium.SOCKETS.toString(),
                        EnvVarConstants.DATA_CHANNEL_SOCKET_PATHS to
                            socketWriters.joinToString(",") { it.socketPath }
                    )
                }
            }

        destination =
            CliRunner.destination(
                command,
                configContents = configContents,
                catalog = catalog,
                inputStream =
                    if (injectInputStream && dataChannelMedium == DataChannelMedium.STDIO) {
                        destinationStdin
                    } else {
                        null
                    },
                featureFlags = featureFlags,
                additionalMicronautEnvs = additionalMicronautEnvs,
                micronautProperties =
                    (micronautProperties + additionalMicronautProperties).mapKeys { (k, _) ->
                        k.micronautProperty
                    },
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
                            destination.results.traces(),
                            destination.results.states(),
                        )
                    }
                    destinationComplete.complete(Unit)
                }
            }
            .invokeOnCompletion { executor.shutdownNow() }
    }

    override suspend fun sendMessage(message: AirbyteMessage, broadcast: Boolean) {
        val messageString = message.serializeToString()
        val channelsToSendTo =
            if (broadcast) {
                destinationStdinPipes
            } else {
                arrayOf(destinationStdinPipes[onChannel.rotate(destinationStdinPipes.size)])
            }
        channelsToSendTo.forEach { it.println(messageString) }
    }

    override suspend fun sendMessage(string: String) {
        destinationStdinPipes[onChannel.rotate(destinationStdinPipes.size)].println(string)
    }

    override fun readMessages(): List<AirbyteMessage> = destination.results.newMessages()

    override suspend fun shutdown() {
        destinationStdinPipes.forEach { it.close() }
        destinationComplete.join()
    }

    override fun kill() {
        // In addition to preventing the executor from accepting new tasks,
        // this also sends a Thread.interrupt() to running tasks.
        // Coroutines interpret this as a cancellation.
        executor.shutdownNow()
    }

    override fun verifyFileDeleted() {
        assertFalse(file.exists())
    }
}

class NonDockerizedDestinationFactory(
    private val additionalMicronautEnvs: List<String>,
) : DestinationProcessFactory() {
    /**
     * In `check` operations, we do some micronaut magic to redirect the input stream. This
     * conflicts with the test bean injection, so we expose an option to disable the bean override.
     */
    var injectInputStream: Boolean = true

    override fun createDestinationProcess(
        command: String,
        configContents: String?,
        catalog: ConfiguredAirbyteCatalog?,
        useFileTransfer: Boolean,
        micronautProperties: Map<Property, String>,
        dataChannelMedium: DataChannelMedium,
        vararg featureFlags: FeatureFlag,
    ): DestinationProcess {
        // TODO pass test name into the destination process
        return NonDockerizedDestination(
            command,
            configContents,
            catalog,
            useFileTransfer,
            additionalMicronautEnvs,
            micronautProperties,
            injectInputStream = injectInputStream,
            dataChannelMedium = dataChannelMedium,
            *featureFlags
        )
    }
}
