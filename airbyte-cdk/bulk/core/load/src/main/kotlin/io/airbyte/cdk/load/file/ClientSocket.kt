/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.InputStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.channels.Channels
import java.nio.channels.SocketChannel

class ClientSocket(
    val socketPath: String,
    private val bufferSizeBytes: Int,
    private val connectWaitDelayMs: Long = 1000L,
    private val connectTimeoutMs: Long = 15 * 60 * 1000L,
) {
    private val log = KotlinLogging.logger {}

    fun openInputStream(): InputStream {
        log.info { "Connecting client socket at $socketPath" }
        val socketFile = File(socketPath)
        var totalWaitMs = 0L

        while (!socketFile.exists()) {
            log.info { "Waiting for socket file to be created: $socketPath" }
            Thread.sleep(connectWaitDelayMs)
            totalWaitMs += connectWaitDelayMs
            if (totalWaitMs > connectTimeoutMs) {
                throw IllegalStateException(
                    "Socket file $socketPath not created after $connectTimeoutMs ms"
                )
            }
        }
        log.info { "Socket file $socketPath created" }

        val address = UnixDomainSocketAddress.of(socketFile.toPath())
        val openedSocket = SocketChannel.open(StandardProtocolFamily.UNIX)

        log.info { "Socket file $socketPath opened" }

        if (!openedSocket.connect(address)) {
            throw IllegalStateException("Failed to connect to socket $socketPath")
        }

        // HACK: The dockerized destination tests uses this exact message
        // as a signal that it's safe to create the TCP connection to the
        // socat sidecar that feeds data into the socket. Removing it
        // will break tests. TODO: Anything else.
        log.info { "Socket file $socketPath connected for reading" }

        return Channels.newInputStream(openedSocket).buffered(bufferSizeBytes)
    }
}
