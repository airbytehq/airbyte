/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import com.google.common.collect.Lists
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.nio.file.Files
import java.nio.file.Path
import java.util.Locale
import org.apache.commons.lang3.RandomStringUtils

private val logger = KotlinLogging.logger {}

// TODO define a factory for this class + @Require(env = CI_master_merge)
class DockerizedDestination(
    private val imageName: String,
    private val command: String,
    private val config: ConfigurationSpecification?,
    private val catalog: ConfiguredAirbyteCatalog?,
    private val testDeploymentMode: TestDeploymentMode,
) : DestinationProcess {
    private lateinit var process: Process

    override fun run() {
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

        val randomSuffix =
            RandomStringUtils.insecure()
                .nextAlphanumeric(5)
                .lowercase(Locale.getDefault())
        // Extract "destination-foo" from "gcr.io/airbyte/destination-foo:1.2.3"
        // The old code had a ton of extra logic here, along with a max string
        // length (docker container names must be <128 chars) - none of that
        // seems necessary here.
        // And platform doesn't even follow that convention anymore, now that
        // we have monopods. (the pod has a name like replication-job-18386126-attempt-4,
        // and the destination container is just called "destination")
        val shortImageName =
            imageName.substringAfterLast("/").substringBefore(":")
        val containerName = "$shortImageName-$command-$randomSuffix"
        logger.info { "Creating docker container $containerName" }

        val cmd: MutableList<String> =
            Lists.newArrayList(
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
                "-e",
                "DEPLOYMENT_MODE=$testDeploymentMode",
                // Yes, we hardcode the job ID to 0.
                // Also yes, this is available in the configured catalog
                // via the syncId property.
                // Also also yes, we're relying on this env var >.>
                "-e",
                "WORKER_JOB_ID=0",
                imageName,
                command,
            )

        fun addInput(paramName: String, fileContents: Any) {
            Files.write(
                jobRoot.resolve("destination_$paramName.json"),
                Jsons.writeValueAsBytes(fileContents)
            )
            cmd.add("--$paramName")
            cmd.add("destination_$paramName.json")
        }
        config?.let { addInput("config", it) }
        catalog?.let { addInput("catalog", it) }

        logger.info { "Executing command: ${cmd.joinToString(" ")}" }
        process = ProcessBuilder(cmd).start()
    }

    override fun sendMessage(message: AirbyteMessage) {
        // push a message to the docker process' stdin
        TODO("Not yet implemented")
    }

    override fun readMessages(): List<AirbyteMessage> {
        // read everything from the process' stdout
        TODO("Not yet implemented")
    }

    override fun shutdown() {
        // close stdin, wait until process exits
        TODO("Not yet implemented")
    }
}

// This is currently unused, but we'll need it for the Docker version.
// it exists right now b/c I wrote it prior to the CliRunner retooling.
/**
 * There doesn't seem to be a built-in equivalent to this? Scanner and BufferedReader both have
 * `hasNextLine` methods which block until the stream has data to read, which we don't want to do.
 *
 * This class simply buffers the next line in-memory until it reaches a newline or EOF.
 */
private class LazyInputStreamReader(private val input: InputStream) {
    private val buffer: ByteArrayOutputStream = ByteArrayOutputStream()
    private var eof = false

    /**
     * Returns the next line of data, or null if no line is available. Doesn't block if the
     * inputstream has no data.
     */
    fun nextLine(): MaybeLine {
        if (eof) {
            return NoLine.EOF
        }
        while (input.available() != 0) {
            when (val read = input.read()) {
                -1 -> {
                    eof = true
                    val line = Line(buffer.toByteArray().toString(Charsets.UTF_8))
                    buffer.reset()
                    return line
                }
                '\n'.code -> {
                    val bytes = buffer.toByteArray()
                    buffer.reset()
                    return Line(bytes.toString(Charsets.UTF_8))
                }
                else -> {
                    buffer.write(read)
                }
            }
        }
        return NoLine.NOT_YET_AVAILABLE
    }

    companion object {
        sealed interface MaybeLine
        enum class NoLine : MaybeLine {
            EOF,
            NOT_YET_AVAILABLE
        }
        data class Line(val line: String) : MaybeLine
    }
}
