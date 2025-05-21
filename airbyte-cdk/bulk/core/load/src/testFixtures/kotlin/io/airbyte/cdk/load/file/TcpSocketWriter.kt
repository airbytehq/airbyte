/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.OutputStream
import java.net.InetSocketAddress
import java.net.Socket

/**
 * An OutputStream that writes directly to a TCP port. Used by the Dockerized destination for
 * socket-based testing, since MacOS Docker doesn't support sharing Unix domain sockets between the
 * host and the container.
 */
class TCPSocketWriter(
    private val host: String,
    private val port: Int,
    awaitFirstWrite: Boolean,
) : OutputStream(), AutoCloseable {
    private val log = KotlinLogging.logger {}

    private val socket = Socket()
    private var outputStream: OutputStream? = null

    init {
        if (!awaitFirstWrite) {
            connect()
        }
    }

    private fun connect() {
        log.info { "Connecting to TCP socket at $host:$port" }
        // This is a hack due to the fact that there is a slight delay between
        // the only signal we have for socat availability (the destination
        // successfully connecting to the UNIX socket) and the TCP socket
        // becoming available. In practice, this is enough time even if I
        // run every single test in parallel in socket mode.
        // See the DockerizedDestinationFactory sidecar for more details.
        Thread.sleep(1000L)
        socket.connect(InetSocketAddress(host, port), 0)
        outputStream = socket.getOutputStream().buffered()
    }

    override fun write(b: Int) {
        outputStream ?: connect()
        outputStream!!.write(b)
    }

    override fun write(b: ByteArray, off: Int, len: Int) {
        outputStream ?: connect()
        outputStream!!.write(b, off, len)
    }

    override fun flush() {
        outputStream ?: connect()
        outputStream!!.flush()
    }

    override fun close() {
        log.info { "Closing TCP socket writer for $host:$port" }
        outputStream ?: connect()
        outputStream!!.close()
    }
}
