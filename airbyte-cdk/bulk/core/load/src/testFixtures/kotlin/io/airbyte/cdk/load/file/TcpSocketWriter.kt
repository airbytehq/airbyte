/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.OutputStream
import java.net.InetSocketAddress
import java.net.Socket
import java.time.Duration

/**
 * An OutputStream that writes directly to a TCP port. Used by the Dockerized destination for
 * socket-based testing, since MacOS Docker doesn't support sharing Unix domain sockets between the
 * host and the container.
 */
class TCPSocketWriter(
    private val host: String,
    private val port: Int,
    private val awaitFirstWrite: Boolean,
    private val connectTimeout: Duration = Duration.ofSeconds(5)
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
        Thread.sleep(1000L) // Avoid socat race condition
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
