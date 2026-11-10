/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.InputStream
import java.net.ConnectException
import java.net.SocketException
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.channels.Channels
import java.nio.channels.SocketChannel
import kotlin.time.TimeSource

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
        val address = UnixDomainSocketAddress.of(socketFile.toPath())
        val start = TimeSource.Monotonic.markNow()
        var lastFailure: SocketException? = null

        do {
            if (socketFile.exists()) {
                log.info { "Socket file $socketPath created" }
                try {
                    val openedSocket = SocketChannel.open(StandardProtocolFamily.UNIX)
                    try {
                        log.info { "Socket file $socketPath opened" }
                        check(openedSocket.connect(address)) {
                            "Failed to connect to socket $socketPath"
                        }

                        // Dockerized destination tests use this exact message as a readiness
                        // signal.
                        log.info { "Socket file $socketPath connected for reading" }

                        return Channels.newInputStream(openedSocket).buffered(bufferSizeBytes)
                    } catch (e: Exception) {
                        openedSocket.close()
                        throw e
                    }
                } catch (e: SocketException) {
                    if (e !is ConnectException && socketFile.exists()) {
                        throw e
                    }
                    lastFailure = e
                    log.info { "Socket file $socketPath is not ready for reading; retrying" }
                }
            } else {
                log.info { "Waiting for socket file to be created: $socketPath" }
            }

            val remainingMs = connectTimeoutMs - start.elapsedNow().inWholeMilliseconds
            if (remainingMs <= 0) {
                break
            }
            Thread.sleep(minOf(connectWaitDelayMs, remainingMs))
        } while (start.elapsedNow().inWholeMilliseconds < connectTimeoutMs)

        throw IllegalStateException(
            "Socket $socketPath not ready for reading after $connectTimeoutMs ms",
            lastFailure,
        )
    }
}
