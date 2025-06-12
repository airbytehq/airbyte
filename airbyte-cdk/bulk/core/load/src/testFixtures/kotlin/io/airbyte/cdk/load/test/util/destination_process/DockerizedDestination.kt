/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import TCPSocketWriter
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.extensions.grantAllPermissions
import io.airbyte.cdk.load.command.EnvVarConstants
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.config.NamespaceMappingConfig
import io.airbyte.cdk.load.file.TcpPortReserver
import io.airbyte.cdk.load.message.InputMessage
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.NUM_SOCKETS
import io.airbyte.cdk.load.test.util.rotate
import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.OutputStream
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths
import java.time.Clock
import java.util.*
import java.util.concurrent.atomic.AtomicInteger
import kotlin.io.path.outputStream
import kotlin.io.path.writeText
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.yield
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Assertions.assertFalse

private val logger = KotlinLogging.logger {}

// TODO define a factory for this class + @Require(env = CI_master_merge)
class DockerizedDestination(
    private val imageTag: String,
    private val command: String,
    private val configContents: String?,
    private val catalog: ConfiguredAirbyteCatalog?,
    private val testName: String,
    private val useFileTransfer: Boolean,
    private val envVars: Map<String, String>,
    override val dataChannelMedium: DataChannelMedium,
    val dataChannelFormat: DataChannelFormat,
    val namespaceMappingConfig: NamespaceMappingConfig,
    vararg featureFlags: FeatureFlag,
) : DestinationProcess {
    private val process: Process
    private var sidecarProcess: Process? = null
    private val destinationOutput = BufferingOutputConsumer(Clock.systemDefaultZone())
    private val destinationDataChannels: Array<OutputStream>
    // We use this suffix as part of the docker container name.
    // We'll also add it to the log prefix, which helps with debugging tests
    // that launch multiple containers.
    private val randomSuffix =
        RandomStringUtils.insecure().nextAlphanumeric(5).lowercase(Locale.getDefault())

    private fun getMdcScope(): TestConnectorMdcScope =
        TestConnectorMdcScope("$testName-$randomSuffix")

    private val stdoutDrained = CompletableDeferred<Unit>()
    private val stderrDrained = CompletableDeferred<Unit>()
    // Mainly, used for file transfer but there are other consumers, name the AWS CRT HTTP client.
    private val tmpDir = Files.createTempDirectory("tmp").grantAllPermissions()
    private val socketPathDir = "/var/airbyte"
    private val sharedVolumeName = "airbyte-test-shared-volume-$randomSuffix"
    private val destinationAwaitingSocketConnection = CompletableDeferred<Unit>()
    private val dataChannelIndex = AtomicInteger(0)

    init {
        createSharedVolume()
        process = startDestination(featureFlags)

        // Annoyingly, the process's stdin is called "outputStream"
        destinationDataChannels =
            when (dataChannelMedium) {
                DataChannelMedium.STDIO -> arrayOf(process.outputStream)
                DataChannelMedium.SOCKET -> {
                    (0 until NUM_SOCKETS)
                        .map {
                            val sidecarPort = TcpPortReserver.findAvailablePort()
                            sidecarProcess = startSidecar(sidecarPort, makeSocketPath(it), it)

                            TCPSocketWriter("localhost", sidecarPort, awaitFirstWrite = true)
                        }
                        .toTypedArray()
                }
            }
    }

    private fun makeSocketPath(socketIndex: Int): String =
        "$socketPathDir/ab_socket_${randomSuffix}_$socketIndex.socket"

    private fun createSharedVolume() {
        val createVolumeCommand =
            listOf(
                "docker",
                "volume",
                "create",
                "--name",
                sharedVolumeName,
            )
        logger.info { "Creating shared volume $sharedVolumeName" }
        ProcessBuilder(createVolumeCommand).start().waitFor()
    }

    private fun startDestination(featureFlags: Array<out FeatureFlag>): Process {
        // This is largely copied from the old cdk's DockerProcessFactory /
        // AirbyteIntegrationLauncher / DestinationAcceptanceTest,
        // but cleaned up, consolidated, and simplified.
        // Those classes included a ton of logic that is only useful for
        // the actual platform, and we don't need it here.
        val testDir = Path.of("/tmp/airbyte_tests/")
        Files.createDirectories(testDir)
        // Allow ourselves and our connector access to our test dir
        testDir.grantAllPermissions()
        val workspaceRoot = Files.createTempDirectory(testDir, "test")
        workspaceRoot.grantAllPermissions()

        // This directory will contain the actual inputs to the connector (config+catalog),
        // and is also mounted as a volume.
        val jobDir = "job"
        val jobRoot = Files.createDirectories(workspaceRoot.resolve(jobDir))
        jobRoot.grantAllPermissions()

        val containerDataRoot = "/data"
        val containerJobRoot = "$containerDataRoot/$jobDir"

        // This directory is being used for the file transfer feature.
        if (useFileTransfer) {
            val file = Files.createFile(tmpDir.resolve("test_file"))
            file.writeText("123")
        }
        // Extract the string "destination-foo" from "gcr.io/airbyte/destination-foo:1.2.3".
        // The old code had a ton of extra logic here, along with a max string
        // length (docker container names must be <128 chars) - none of that
        // seems necessary here.
        // And platform doesn't even follow that convention anymore, now that
        // we have monopods. (the pod has a name like replication-job-18386126-attempt-4,
        // and the destination container is just called "destination")
        val shortImageName = imageTag.substringAfterLast("/").substringBefore(":")
        val containerName = "$shortImageName-$command-$randomSuffix"
        logger.info { "Creating docker container $containerName" }
        logger.info { "File transfer ${if (useFileTransfer) "is " else "isn't"} enabled" }

        val containerNamespaceMapperConfigPath =
            Paths.get(containerDataRoot, "namespace-mapper-config.json")
        val hostNamespaceMapperConfigPath = workspaceRoot.resolve("namespace-mapper-config.json")
        hostNamespaceMapperConfigPath.outputStream().use {
            it.write(namespaceMappingConfig.serializeToJsonBytes())
        }
        val socketPaths = (0 until NUM_SOCKETS).joinToString(",") { makeSocketPath(it) }
        val socketPathEnvVarsMaybe =
            if (dataChannelMedium == DataChannelMedium.SOCKET) {
                listOf(
                    "-e",
                    "${EnvVarConstants.DATA_CHANNEL_MEDIUM.environmentVariable}=${DataChannelMedium.SOCKET}",
                    "-e",
                    "${EnvVarConstants.DATA_CHANNEL_FORMAT.environmentVariable}=$dataChannelFormat",
                    "-e",
                    "${EnvVarConstants.DATA_CHANNEL_SOCKET_PATHS.environmentVariable}=$socketPaths",
                    "-e",
                    "${EnvVarConstants.NAMESPACE_MAPPER_CONFIG_PATH.environmentVariable}=$containerNamespaceMapperConfigPath",
                )
            } else {
                emptyList()
            }

        val additionalEnvEntries =
            envVars.flatMap { (key, value) ->
                logger.info { "Env vars: $key loaded" }
                listOf("-e", "$key=$value")
            } + socketPathEnvVarsMaybe

        // DANGER: env vars can contain secrets, so you MUST NOT log this command.
        val cmd: MutableList<String> =
            (listOf(
                    "docker",
                    "run",
                    "--rm",
                    "--init",
                    "-i",
                    "-w",
                    // In real syncs, platform changes the workdir to /dest for destinations.
                    testDir.toString(),
                    "--log-driver",
                    "none",
                    "--name",
                    containerName,
                    "--mount",
                    "source=$sharedVolumeName,target=/var/airbyte",
                    "-v",
                    String.format("%s:%s", workspaceRoot, containerDataRoot),
                    "-v",
                    "$tmpDir:/tmp",
                ) +
                    additionalEnvEntries +
                    featureFlags.flatMap { listOf("-e", it.envVarBindingDeclaration) } +
                    listOf(
                        // Yes, we hardcode the job ID to 0.
                        // Also yes, this is available in the configured catalog
                        // via the syncId property.
                        // Also also yes, we're relying on this env var >.>
                        "-e",
                        "WORKER_JOB_ID=0",
                        imageTag,
                        command
                    ))
                .toMutableList()

        fun addInput(paramName: String, fileContents: ByteArray) {
            val path = jobRoot.resolve("destination_$paramName.json")
            Files.write(
                path,
                fileContents,
            )
            path.grantAllPermissions()

            cmd.add("--$paramName")
            cmd.add("$containerJobRoot/destination_$paramName.json")
        }
        configContents?.let { addInput("config", it.toByteArray(Charsets.UTF_8)) }
        catalog?.let { addInput("catalog", catalog.serializeToJsonBytes()) }

        logger.info { "Running destination with command: $cmd" }
        return ProcessBuilder(cmd).start()
    }

    private fun startSidecar(sidecarPort: Int, socketPath: String, index: Int): Process {
        // Starts the socat container first, which creates the socket with proper permissions
        // UNIX-LISTEN ensures socat will create the UNIX socket. It will also await connections
        // and block until a connection is made.
        // TCP-LISTEN will create a TCP socket that forwards to the UNIX socket. It will only
        // start accepting connections after the UNIX socket connection. Connections made sooner
        // will silently fail. (Either by blocking on write or by devnulling the data. I have no
        // idea why
        // this happens. In practice tests will hang or destinations will throw as if having
        // received EOF before end-of-stream.)
        //
        // In theory we should be able to make the TCP port available sooner by `fork`ing the UNIX
        // call, but in practice the TCP connection will still silently fail if the destination
        // hasn't connected to
        // the socket yet. To hack around this, we A) lazily initialize the TCP socket connection on
        // first write and B) block writes until the destination logs that it has successfully
        // connected. THIS IS HORRIBLE AND WILL PROBABLY BREAK IN A CONFUSING WAY.
        //
        // NOTE: There is also a slight delay between the destination connecting to the UNIX socket
        // and the TCP port being available. To hack around that the TcpSocketWriter waits an extra
        // second before connecting. In practice this seems sufficient even when running 100s of
        // tests concurrently. (Without it about 3-4 of the total will hang indefinitely.)
        val socatCommand =
            listOf(
                "docker",
                "run",
                "--rm",
                "-d",
                "--name",
                "socat-sidecar-$randomSuffix-$index",
                "--mount",
                "source=$sharedVolumeName,target=/var/airbyte",
                "-p",
                "$sidecarPort:$sidecarPort",
                "alpine/socat",
                // level of logging; more d's => more verbose. At 15 it becomes sentient.
                "-dddd",
                "UNIX-LISTEN:$socketPath,reuseaddr,mode=777",
                "TCP-LISTEN:$sidecarPort,reuseaddr,nodelay=1",
            )
        logger.info { "Starting socat sidecar with command: $socatCommand" }
        return ProcessBuilder(socatCommand).start()
    }

    private fun removeSharedVolume() {
        val removeVolumeCommand =
            listOf(
                "docker",
                "volume",
                "rm",
                sharedVolumeName,
            )
        logger.info { "Removing shared volume $sharedVolumeName" }
        ProcessBuilder(removeVolumeCommand).start().waitFor()
    }

    private suspend fun awaitReadyForSendingMessages() {
        if (dataChannelMedium == DataChannelMedium.SOCKET) {
            destinationAwaitingSocketConnection.await()
        }
    }

    override suspend fun run() {
        coroutineScope {
                launch {
                    // Consume stdout. These should all be properly-formatted messages.
                    // Annoyingly, the process's stdout is called "inputStream".
                    val destinationStdout = Scanner(process.inputStream, Charsets.UTF_8)
                    val unconnectedSockets =
                        (0 until NUM_SOCKETS).map { makeSocketPath(it) }.toMutableSet()
                    while (destinationStdout.hasNextLine()) {
                        val line = destinationStdout.nextLine()
                        val message =
                            try {
                                line.deserializeToClass(AirbyteMessage::class.java)
                            } catch (e: Exception) {
                                // If a destination logs non-json output, just echo it
                                getMdcScope().use { logger.info { line } }
                                continue
                            }
                        if (message.type == AirbyteMessage.Type.LOG) {
                            // Don't capture logs, just echo them directly to our own stdout
                            val connectedSockets =
                                unconnectedSockets.filter {
                                    message.log.message.contains(
                                        "Socket file $it connected for reading"
                                    )
                                }
                            connectedSockets.forEach {
                                // This is a hack to detect when the destination is ready to accept
                                // messages.
                                // We should probably find a better way to do this.
                                unconnectedSockets.remove(it)
                                if (unconnectedSockets.isEmpty()) {
                                    logger.info { "All sockets connected, unblocking writes." }
                                    destinationAwaitingSocketConnection.complete(Unit)
                                }
                            }

                            val combinedMessage =
                                message.log.message +
                                    (if (message.log.stackTrace != null)
                                        (System.lineSeparator() +
                                            "Stack Trace: " +
                                            message.log.stackTrace)
                                    else "")
                            getMdcScope().use {
                                when (message.log.level) {
                                    null, // this should be impossible, treat it as error
                                    AirbyteLogMessage.Level
                                        .FATAL, // klogger doesn't have a fatal level
                                    AirbyteLogMessage.Level.ERROR ->
                                        logger.error { combinedMessage }
                                    AirbyteLogMessage.Level.WARN -> logger.warn { combinedMessage }
                                    AirbyteLogMessage.Level.INFO -> logger.info { combinedMessage }
                                    AirbyteLogMessage.Level.DEBUG ->
                                        logger.debug { combinedMessage }
                                    AirbyteLogMessage.Level.TRACE ->
                                        logger.trace { combinedMessage }
                                }
                            }
                        } else {
                            destinationOutput.accept(message)
                        }
                        // Explicit yield to avoid blocking
                        yield()
                    }
                    stdoutDrained.complete(Unit)
                }
                launch {
                    // Consume stderr. Connectors shouldn't really use this,
                    // and whatever this stream contains, it's almost certainly not valid messages.
                    // Dump it straight to our own stderr.
                    getMdcScope().use {
                        process.errorReader().lineSequence().forEach {
                            logger.error { it }
                            yield()
                        }
                    }
                    stderrDrained.complete(Unit)
                }
            }
            .invokeOnCompletion { cause ->
                if (cause != null) {
                    if (process.isAlive) {
                        logger.info(cause) { "Destroying process due to exception" }
                        process.destroyForcibly()
                    }
                }
            }
    }

    override suspend fun sendMessage(message: InputMessage, broadcast: Boolean) {
        awaitReadyForSendingMessages()
        val dataChannels =
            if (broadcast) {
                destinationDataChannels
            } else {
                arrayOf(
                    destinationDataChannels[dataChannelIndex.rotate(destinationDataChannels.size)]
                )
            }
        dataChannels.forEach { message.writeProtocolMessage(dataChannelFormat, it) }
    }

    override suspend fun sendMessage(string: String) {
        awaitReadyForSendingMessages()
        destinationDataChannels[dataChannelIndex.rotate(destinationDataChannels.size)].let {
            it.write(string.toByteArray(Charsets.UTF_8))
            it.write('\n'.code)
        }
    }

    override fun readMessages(): List<AirbyteMessage> {
        return destinationOutput.newMessages()
    }

    override suspend fun shutdown() {
        withContext(Dispatchers.IO) {
            logger.info { "Destination $randomSuffix shutting down" }
            destinationDataChannels.forEach { it.close() }
            // Wait for ourselves to drain stdout/stderr. Otherwise we won't capture
            // all the destination output (logs/trace messages).
            stdoutDrained.join()
            stderrDrained.join()

            // The old cdk had a 1-minute timeout here. That seems... weird?
            // We can just rely on the junit timeout, presumably?
            process.waitFor()
            val exitCode = process.exitValue()
            if (exitCode != 0) {
                throw DestinationUncleanExitException.of(
                    exitCode,
                    destinationOutput.traces(),
                    destinationOutput.states(),
                )
            }
            removeSharedVolume()
        }
    }

    override suspend fun kill() {
        process.destroyForcibly()
    }

    override fun verifyFileDeleted() {
        val file = File(tmpDir.resolve("test_file").toUri())
        assertFalse(file.exists())
    }
}

class DockerizedDestinationFactory(
    private val imageName: String,
    private val imageVersion: String,
) : DestinationProcessFactory() {
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
        return DockerizedDestination(
            "$imageName:$imageVersion",
            command,
            configContents,
            catalog,
            testName,
            useFileTransfer,
            micronautProperties.mapKeys { (k, _) -> k.environmentVariable },
            dataChannelMedium,
            dataChannelFormat,
            namespaceMappingConfig = namespaceMappingConfig,
            *featureFlags,
        )
    }
}
