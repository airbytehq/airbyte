/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.io.ByteArrayOutputStream
import java.io.InputStream

// TODO define a factory for this class + @Require(env = CI_master_merge)
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
