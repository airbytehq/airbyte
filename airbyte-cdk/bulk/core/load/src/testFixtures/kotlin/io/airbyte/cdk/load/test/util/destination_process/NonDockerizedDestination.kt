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
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.config.NamespaceMappingConfig
import io.airbyte.cdk.load.file.ServerSocketWriterOutputStream
import io.airbyte.cdk.load.message.InputMessage
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.NUM_SOCKETS
import io.airbyte.cdk.load.test.util.rotate
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.InputStream
import java.io.OutputStream
import java.io.PipedInputStream
import java.io.PipedOutputStream
import java.nio.file.Files
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicInteger
import kotlin.io.path.outputStream
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
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
    val dataChannelFormat: DataChannelFormat,
    val namespaceMappingConfig: NamespaceMappingConfig,
    vararg featureFlags: FeatureFlag,
) : DestinationProcess {
    private val destinationDataChannels: Array<OutputStream>
    private val onChannel = AtomicInteger(0)
    private val destination: CliRunnable
    private val destinationComplete = CompletableDeferred<Unit>()
    // The destination has a runBlocking inside WriteOperation.
    // This means that normal coroutine cancellation doesn't work.
    // So we start our own thread pool, which we can forcibly kill if needed.
    private val executor = Executors.newFixedThreadPool(4)
    private val coroutineDispatcher = executor.asCoroutineDispatcher()
    private val file = File("/tmp/test_file")
    private val writeLock = Mutex()
    private val namespaceMappingConfigPath =
        Files.createTempFile("namespace_mapping_config", ".json")

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
                    destinationDataChannels = arrayOf(PipedOutputStream(destinationStdin))
                    mapOf(
                        EnvVarConstants.DATA_CHANNEL_MEDIUM to DataChannelMedium.STDIO.toString(),
                    )
                }
                DataChannelMedium.SOCKET -> {
                    val socketWriters =
                        (0 until NUM_SOCKETS).map {
                            val socketFile = File.createTempFile("ab_socket_${it}_", ".socket")
                            socketFile.delete()
                            ServerSocketWriterOutputStream(socketFile.path.toString())
                        }
                    destinationDataChannels = socketWriters.toTypedArray()
                    namespaceMappingConfigPath.outputStream().use { outputStream ->
                        outputStream.write(namespaceMappingConfig.serializeToJsonBytes())
                    }
                    mapOf(
                        EnvVarConstants.DATA_CHANNEL_MEDIUM to DataChannelMedium.SOCKET.toString(),
                        EnvVarConstants.DATA_CHANNEL_FORMAT to dataChannelFormat.toString(),
                        EnvVarConstants.DATA_CHANNEL_SOCKET_PATHS to
                            socketWriters.joinToString(",") { it.socketPath },
                        EnvVarConstants.NAMESPACE_MAPPER_CONFIG_PATH to
                            namespaceMappingConfigPath.toString()
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
                    } finally {
                        destinationComplete.complete(Unit)
                    }
                }
            }
            .invokeOnCompletion { executor.shutdownNow() }
    }

    override suspend fun sendMessage(string: String) {
        writeLock.withLock {
            destinationDataChannels[onChannel.rotate(destinationDataChannels.size)].write(
                string.toByteArray()
            )
        }
    }

    override suspend fun sendMessage(message: InputMessage, broadcast: Boolean) {
        writeLock.withLock {
            val channelsToSendTo =
                if (broadcast) {
                    destinationDataChannels
                } else {
                    arrayOf(destinationDataChannels[onChannel.rotate(destinationDataChannels.size)])
                }
            channelsToSendTo.forEach { message.writeProtocolMessage(dataChannelFormat, it) }
        }
    }

    override fun readMessages(): List<AirbyteMessage> = destination.results.newMessages()

    override suspend fun shutdown() {
        destinationDataChannels.forEach { writeLock.withLock { it.close() } }
        destinationComplete.join()
    }

    override suspend fun kill() {
        destinationDataChannels.forEach { writeLock.withLock { it.close() } }
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
        dataChannelFormat: DataChannelFormat,
        namespaceMappingConfig: NamespaceMappingConfig,
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
            dataChannelFormat = dataChannelFormat,
            namespaceMappingConfig = namespaceMappingConfig,
            *featureFlags
        )
    }
}
