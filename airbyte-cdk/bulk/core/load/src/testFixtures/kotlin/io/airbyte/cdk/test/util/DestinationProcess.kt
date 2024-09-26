/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.util

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.PipedInputStream
import java.io.PipedOutputStream
import java.io.PrintWriter
import javax.inject.Singleton

private val logger = KotlinLogging.logger {}

/**
 * Represents a destination process, whether running in-JVM via micronaut, or as a separate Docker
 * container. The general lifecycle is:
 * 1. `val dest = DestinationProcessFactory.createDestinationProcess(...)`
 * 2. `launch { dest.run() }`
 * 3. [sendMessage] as many times as you want
 * 4. [readMessages] as needed (e.g. to check that state messages are emitted during the sync)
 * 5. [shutdown] once you have no more messages to send to the destination
 */
interface DestinationProcess {
    /**
     * Run the destination process. Callers who want to interact with the destination should
     * `launch` this method.
     */
    fun run()

    fun sendMessage(message: AirbyteMessage)

    /** Return all messages the destination emitted since the last call to [readMessages]. */
    fun readMessages(): List<AirbyteMessage>

    /**
     * Wait for the destination to terminate, then return all messages it emitted since the last
     * call to [readMessages].
     */
    fun shutdown()
}

interface DestinationProcessFactory {
    fun createDestinationProcess(
        command: String,
        config: ConfigurationJsonObjectBase? = null,
        catalog: ConfiguredAirbyteCatalog? = null,
    ): DestinationProcess
}

class NonDockerizedDestination(
    command: String,
    config: ConfigurationJsonObjectBase?,
    catalog: ConfiguredAirbyteCatalog?,
) : DestinationProcess {
    private val destinationStdinPipe: PrintWriter
    private val destination: CliRunnable

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
                config = config,
                catalog = catalog,
                inputStream = destinationStdin,
            )
    }

    override fun run() {
        destination.run()
    }

    override fun sendMessage(message: AirbyteMessage) {
        destinationStdinPipe.println(Jsons.serialize(message))
    }

    override fun readMessages(): List<AirbyteMessage> = destination.results.newMessages()

    override fun shutdown() {
        destinationStdinPipe.close()
    }
}

// Notably, not actually a Micronaut factory. We want to inject the actual
// factory into our tests, not a pre-instantiated destination, because we want
// to run multiple destination processes per test.
// TODO only inject this when not running in CI, a la @Requires(notEnv = "CI_master_merge")
@Singleton
class NonDockerizedDestinationFactory : DestinationProcessFactory {
    override fun createDestinationProcess(
        command: String,
        config: ConfigurationJsonObjectBase?,
        catalog: ConfiguredAirbyteCatalog?
    ): DestinationProcess {
        return NonDockerizedDestination(command, config, catalog)
    }
}

// TODO define a factory for this class + @Require(env = CI_master_merge)
// suppress the unused argument warnings in the kotlin compiler
class DockerizedDestination(
    val command: String,
    val config: JsonNode?,
    val catalog: ConfiguredAirbyteCatalog?,
) : DestinationProcess {
    override fun run() {
        TODO("launch a docker container")
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
        interface MaybeLine
        enum class NoLine : MaybeLine {
            EOF,
            NOT_YET_AVAILABLE
        }
        data class Line(val line: String) : MaybeLine
    }
}
