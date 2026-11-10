/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.mockk.every
import io.mockk.mockkStatic
import java.io.InputStream
import java.net.ConnectException
import java.net.SocketException
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.ByteBuffer
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.nio.file.Files
import java.nio.file.Path
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.io.TempDir
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

@Timeout(10)
class ClientSocketTest {
    @TempDir lateinit var directory: Path

    @Test
    fun `coroutine retry is cancellable and closes the failed channel`() = runBlocking {
        staleSocket()
        SocketChannel.open(StandardProtocolFamily.UNIX).use { channel ->
            mockkStatic(SocketChannel::class) {
                every { SocketChannel.open(StandardProtocolFamily.UNIX) } returns channel
                val client = ClientSocket(socketPath.toString(), 16, 10000, 60000)
                val job =
                    launch(start = CoroutineStart.UNDISPATCHED) {
                        client.connect { error("No listener is available") }
                    }
                job.cancelAndJoin()
                assertTrue(job.isCancelled)
                assertFalse(channel.isOpen)
            }
        }
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `retries if the socket file disappears before connecting`(useConnect: Boolean) {
        staleSocket()
        SocketChannel.open(StandardProtocolFamily.UNIX).use { channel ->
            mockkStatic(SocketChannel::class) {
                every { SocketChannel.open(StandardProtocolFamily.UNIX) } answers
                    {
                        Files.delete(socketPath)
                        channel
                    }
                val client = ClientSocket(socketPath.toString(), 16, 1, 20)
                val error =
                    assertThrows(IllegalStateException::class.java) {
                        runBlocking {
                            consume(client, useConnect) { error("No listener is available") }
                        }
                    }
                assertInstanceOf(SocketException::class.java, error.cause)
                assertFalse(channel.isOpen)
            }
        }
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `does not retry other socket errors while the file exists`(useConnect: Boolean) {
        staleSocket()
        mockkStatic(SocketChannel::class) {
            val failure = SocketException("Permission denied")
            every { SocketChannel.open(StandardProtocolFamily.UNIX) } throws failure
            val client = ClientSocket(socketPath.toString(), 16, 1, 2000)
            val error =
                assertThrows(SocketException::class.java) {
                    runBlocking { consume(client, useConnect) { error("Cannot open the socket") } }
                }
            assertTrue(error === failure)
        }
    }

    @Test
    fun `blocking wait is interruptible`() {
        val client = ClientSocket(socketPath.toString(), 16, 10000, 60000)
        try {
            Thread.currentThread().interrupt()
            assertThrows(InterruptedException::class.java) { client.openInputStream() }
        } finally {
            Thread.interrupted()
        }
    }

    private val socketPath: Path
        get() = directory.resolve("socket")

    private fun staleSocket() {
        ServerSocketChannel.open(StandardProtocolFamily.UNIX).use {
            it.bind(UnixDomainSocketAddress.of(socketPath))
        }
        assertTrue(Files.exists(socketPath))
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `retries refused connections with fresh channels until listener is ready`(
        useConnect: Boolean,
    ) = runBlocking {
        staleSocket()
        val channels = List(3) { SocketChannel.open(StandardProtocolFamily.UNIX) }
        ServerSocketChannel.open(StandardProtocolFamily.UNIX).use { server ->
            try {
                mockkStatic(SocketChannel::class) {
                    var attempts = 0
                    every { SocketChannel.open(StandardProtocolFamily.UNIX) } answers
                        {
                            if (attempts == 2) {
                                Files.delete(socketPath)
                                server.bind(UnixDomainSocketAddress.of(socketPath))
                            }
                            channels[attempts++]
                        }

                    val client = ClientSocket(socketPath.toString(), 16, 1, 2000)
                    consume(client, useConnect) { input ->
                        assertEquals(3, attempts)
                        assertFalse(channels[0].isOpen)
                        assertFalse(channels[1].isOpen)
                        server.accept().use { peer ->
                            peer.write(ByteBuffer.wrap(byteArrayOf(42)))
                        }
                        assertEquals(42, input.read())
                        assertEquals(-1, input.read())
                    }
                    assertFalse(channels[2].isOpen)
                }
            } finally {
                channels.forEach { it.close() }
            }
        }
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `times out if an existing socket never accepts connections`(useConnect: Boolean) {
        staleSocket()
        val client = ClientSocket(socketPath.toString(), 16, 1, 20)
        val error =
            assertThrows(IllegalStateException::class.java) {
                runBlocking { consume(client, useConnect) { error("No listener is available") } }
            }
        assertTrue(error.message!!.contains(socketPath.toString()))
        assertInstanceOf(ConnectException::class.java, error.cause)
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `times out waiting for a missing socket file`(useConnect: Boolean) {
        val client = ClientSocket(socketPath.toString(), 16, 1, 20)
        val error =
            assertThrows(IllegalStateException::class.java) {
                runBlocking { consume(client, useConnect) { error("No socket file is available") } }
            }
        assertTrue(error.message!!.contains(socketPath.toString()))
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `does not retry failures while consuming a connected stream`(useConnect: Boolean) {
        ServerSocketChannel.open(StandardProtocolFamily.UNIX).use { server ->
            server.bind(UnixDomainSocketAddress.of(socketPath))
            val client = ClientSocket(socketPath.toString(), 16, 1, 2000)
            val failure = ConnectException("Consumer failure")
            val error =
                assertThrows(ConnectException::class.java) {
                    runBlocking { consume(client, useConnect) { throw failure } }
                }
            assertTrue(error === failure)
            server.accept().use { assertEquals(-1, it.read(ByteBuffer.allocate(1))) }
        }
    }

    private suspend fun consume(
        client: ClientSocket,
        useConnect: Boolean,
        block: suspend (InputStream) -> Unit,
    ) {
        if (useConnect) {
            client.connect(block)
        } else {
            client.openInputStream().use { block(it) }
        }
    }
}
