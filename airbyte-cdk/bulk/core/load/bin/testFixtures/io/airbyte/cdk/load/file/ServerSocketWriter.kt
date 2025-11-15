/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.OutputStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.channels.Channels.*
import java.nio.channels.ServerSocketChannel

/** Used by the non-dockerized destination to write to a local unix domain socket for testing. */
class ServerSocketWriterOutputStream(
    val socketPath: String,
) : OutputStream() {
    private val log = KotlinLogging.logger {}

    /**
     * This needs to be lazy because otherwise the `accept` call will block on initialization,
     * preventing the test harness from ever getting to the writes.
     */
    private val outputStream: OutputStream by lazy {
        val socketFile = File(socketPath)
        if (socketFile.exists()) {
            log.info { "Deleting existing socket file $socketFile" }
            socketFile.delete()
        }
        log.info { "Creating socket file $socketFile" }
        val address = UnixDomainSocketAddress.of(socketPath)
        log.info { "Opening socket file $socketFile" }
        val serverSocketChannel = ServerSocketChannel.open(StandardProtocolFamily.UNIX)
        serverSocketChannel.bind(address)
        val socketChannel = serverSocketChannel.accept()
        log.info { "Connected to socket $socketFile for writing" }

        newOutputStream(socketChannel)
    }

    override fun write(b: Int) {
        outputStream.write(b)
    }

    override fun close() {
        log.info { "Closing socket file $socketPath" }
        outputStream.close()
    }
}
