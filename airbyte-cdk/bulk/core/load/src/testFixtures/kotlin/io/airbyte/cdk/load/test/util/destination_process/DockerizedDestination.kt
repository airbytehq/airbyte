/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.extensions.grantAllPermissions
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.util.deserializeToClass
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.BufferedWriter
import java.io.File
import java.io.OutputStreamWriter
import java.nio.file.Files
import java.nio.file.Path
import java.time.Clock
import java.util.Locale
import java.util.Scanner
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
    imageTag: String,
    command: String,
    configContents: String?,
    catalog: ConfiguredAirbyteCatalog?,
    private val testName: String,
    useFileTransfer: Boolean,
    envVars: Map<String, String>,
    vararg featureFlags: FeatureFlag,
) : DestinationProcess {
    private val process: Process
    private val destinationOutput = BufferingOutputConsumer(Clock.systemDefaultZone())
    private val destinationStdin: BufferedWriter
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

    init {
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
        val additionalEnvEntries =
            envVars.flatMap { (key, value) ->
                logger.info { "Env vars: $key loaded" }
                listOf("-e", "$key=$value")
            }

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
                    "--network",
                    "host",
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
                        command,
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

        process = ProcessBuilder(cmd).start()
        // Annoyingly, the process's stdin is called "outputStream"
        destinationStdin = BufferedWriter(OutputStreamWriter(process.outputStream, Charsets.UTF_8))
    }

    override suspend fun run() {
        coroutineScope {
                launch {
                    // Consume stdout. These should all be properly-formatted messages.
                    // Annoyingly, the process's stdout is called "inputStream".
                    val destinationStdout = Scanner(process.inputStream, Charsets.UTF_8)
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

    override fun sendMessage(message: AirbyteMessage) {
        destinationStdin.write(message.serializeToString())
        destinationStdin.newLine()
    }

    override fun sendMessage(string: String) {
        destinationStdin.write(string)
        destinationStdin.newLine()
    }

    override fun readMessages(): List<AirbyteMessage> {
        return destinationOutput.newMessages()
    }

    override suspend fun shutdown() {
        withContext(Dispatchers.IO) {
            destinationStdin.close()
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
        }
    }

    override fun kill() {
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
            *featureFlags,
        )
    }
}
