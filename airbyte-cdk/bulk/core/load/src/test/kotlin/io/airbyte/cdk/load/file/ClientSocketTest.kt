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
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.io.TempDir

@Timeout(10)
class ClientSocketTest {
    @TempDir lateinit var directory: Path

    @Test
    fun `retries if the socket file disappears before connecting`() {
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
                        runBlocking { consume(client) { error("No listener is available") } }
                    }
                assertInstanceOf(SocketException::class.java, error.cause)
                assertFalse(channel.isOpen)
            }
        }
    }

    @Test
    fun `does not retry other socket errors while the file exists`() {
        staleSocket()
        mockkStatic(SocketChannel::class) {
            val failure = SocketException("Permission denied")
            every { SocketChannel.open(StandardProtocolFamily.UNIX) } throws failure
            val client = ClientSocket(socketPath.toString(), 16, 1, 2000)
            val error =
                assertThrows(SocketException::class.java) {
                    runBlocking { consume(client) { error("Cannot open the socket") } }
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

    @Test
    fun `retries refused connections with fresh channels until listener is ready`() = runBlocking {
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
                    consume(client) { input ->
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

    @Test
    fun `times out if an existing socket never accepts connections`() {
        staleSocket()
        val client = ClientSocket(socketPath.toString(), 16, 1, 20)
        val error =
            assertThrows(IllegalStateException::class.java) {
                runBlocking { consume(client) { error("No listener is available") } }
            }
        assertTrue(error.message!!.contains(socketPath.toString()))
        assertInstanceOf(ConnectException::class.java, error.cause)
    }

    @Test
    fun `times out waiting for a missing socket file`() {
        val client = ClientSocket(socketPath.toString(), 16, 1, 20)
        val error =
            assertThrows(IllegalStateException::class.java) {
                runBlocking { consume(client) { error("No socket file is available") } }
            }
        assertTrue(error.message!!.contains(socketPath.toString()))
    }

    @Test
    fun `does not retry failures while consuming a connected stream`() {
        ServerSocketChannel.open(StandardProtocolFamily.UNIX).use { server ->
            server.bind(UnixDomainSocketAddress.of(socketPath))
            val client = ClientSocket(socketPath.toString(), 16, 1, 2000)
            val failure = ConnectException("Consumer failure")
            val error =
                assertThrows(ConnectException::class.java) {
                    runBlocking { consume(client) { throw failure } }
                }
            assertTrue(error === failure)
            server.accept().use { assertEquals(-1, it.read(ByteBuffer.allocate(1))) }
        }
    }

    private suspend fun consume(client: ClientSocket, block: suspend (InputStream) -> Unit) {
        client.openInputStream().use { block(it) }
    }
}
