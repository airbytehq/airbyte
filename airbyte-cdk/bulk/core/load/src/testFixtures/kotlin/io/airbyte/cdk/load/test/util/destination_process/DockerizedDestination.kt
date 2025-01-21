/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import java.io.BufferedWriter
import java.io.OutputStreamWriter
import java.nio.file.Files
import java.nio.file.Path
import java.time.Clock
import java.util.Locale
import java.util.Scanner
import javax.inject.Singleton
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.apache.commons.lang3.RandomStringUtils

private val logger = KotlinLogging.logger {}

// TODO define a factory for this class + @Require(env = CI_master_merge)
class DockerizedDestination(
    imageTag: String,
    command: String,
    config: ConfigurationSpecification?,
    catalog: ConfiguredAirbyteCatalog?,
    private val testName: String,
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

    init {
        // This is largely copied from the old cdk's DockerProcessFactory /
        // AirbyteIntegrationLauncher / DestinationAcceptanceTest,
        // but cleaned up, consolidated, and simplified.
        // Those classes included a ton of logic that is only useful for
        // the actual platform, and we don't need it here.
        val testDir = Path.of("/tmp/airbyte_tests/")
        Files.createDirectories(testDir)
        val workspaceRoot = Files.createTempDirectory(testDir, "test")
        // This directory gets mounted to the docker container,
        // presumably so that we can extract some files out of it?
        // It's unclear to me that we actually need to do this...
        // Certainly nothing in the bulk CDK's test suites is reading back
        // anything in this directory.
        val localRoot = Files.createTempDirectory(testDir, "output")
        // This directory will contain the actual inputs to the connector (config+catalog),
        // and is also mounted as a volume.
        val jobRoot = Files.createDirectories(workspaceRoot.resolve("job"))

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

        val cmd: MutableList<String> =
            (listOf(
                    "docker",
                    "run",
                    "--rm",
                    "--init",
                    "-i",
                    "-w",
                    "/data/job",
                    "--log-driver",
                    "none",
                    "--name",
                    containerName,
                    "--network",
                    "host",
                    "-v",
                    String.format("%s:%s", workspaceRoot, "/data"),
                    "-v",
                    String.format("%s:%s", localRoot, "/local"),
                ) +
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

        fun addInput(paramName: String, fileContents: Any) {
            Files.write(
                jobRoot.resolve("destination_$paramName.json"),
                Jsons.writeValueAsBytes(fileContents),
            )
            cmd.add("--$paramName")
            cmd.add("destination_$paramName.json")
        }
        config?.let { addInput("config", it) }
        catalog?.let { addInput("catalog", it) }

        logger.info { "Executing command: ${cmd.joinToString(" ")}" }
        process = ProcessBuilder(cmd).start()
        // Annoyingly, the process's stdin is called "outputStream"
        destinationStdin = BufferedWriter(OutputStreamWriter(process.outputStream, Charsets.UTF_8))
    }

    override suspend fun run() {
        withContext(Dispatchers.IO) {
            launch {
                // Consume stdout. These should all be properly-formatted messages.
                // Annoyingly, the process's stdout is called "inputStream".
                val destinationStdout = Scanner(process.inputStream, Charsets.UTF_8)
                while (destinationStdout.hasNextLine()) {
                    val line = destinationStdout.nextLine()
                    val message =
                        try {
                            Jsons.readValue(line, AirbyteMessage::class.java)
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
                                AirbyteLogMessage.Level.FATAL, // klogger doesn't have a fatal level
                                AirbyteLogMessage.Level.ERROR -> logger.error { combinedMessage }
                                AirbyteLogMessage.Level.WARN -> logger.warn { combinedMessage }
                                AirbyteLogMessage.Level.INFO -> logger.info { combinedMessage }
                                AirbyteLogMessage.Level.DEBUG -> logger.debug { combinedMessage }
                                AirbyteLogMessage.Level.TRACE -> logger.trace { combinedMessage }
                            }
                        }
                    } else {
                        destinationOutput.accept(message)
                    }
                }
                stdoutDrained.complete(Unit)
            }
            launch {
                // Consume stderr. Connectors shouldn't really use this,
                // and whatever this stream contains, it's almost certainly not valid messages.
                // Dump it straight to our own stderr.
                getMdcScope().use { process.errorReader().forEachLine { logger.error { it } } }
                stderrDrained.complete(Unit)
            }
        }
    }

    override fun sendMessage(message: AirbyteMessage) {
        destinationStdin.write(Jsons.writeValueAsString(message))
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
                throw DestinationUncleanExitException.of(exitCode, destinationOutput.traces())
            }
        }
    }
}

@Singleton
@Requires(env = [DOCKERIZED_TEST_ENV])
class DockerizedDestinationFactory(
    // Note that this is not the same property as in MetadataYamlPropertySource.
    // We get this because IntegrationTest manually sets "classpath:metadata.yaml"
    // as a property source.
    // MetadataYamlPropertySource has nothing to do with this property.
    @Value("\${data.docker-repository}") val imageName: String,
    // Most tests will just use micronaut to inject this.
    // But some tests will want to manually instantiate an instance,
    // e.g. to run an older version of the connector.
    // So we just hardcode 'dev' here; manual callers can pass in
    // whatever they want.
    @Value("dev") val imageVersion: String,
) : DestinationProcessFactory() {
    override fun createDestinationProcess(
        command: String,
        config: ConfigurationSpecification?,
        catalog: ConfiguredAirbyteCatalog?,
        vararg featureFlags: FeatureFlag,
    ): DestinationProcess {
        return DockerizedDestination(
            "$imageName:$imageVersion",
            command,
            config,
            catalog,
            testName,
            *featureFlags,
        )
    }
}
