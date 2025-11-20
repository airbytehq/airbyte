/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import io.airbyte.cdk.output.sockets.SocketDataChannel.SocketStatus.SOCKET_READY
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.PropertySource
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.io.OutputStream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test

@MicronautTest
@PropertySource(
    value =
        [
            Property(name = MEDIUM_PROPERTY, value = "SOCKET"),
        ]
)
class SocketDataChannelResourceHolderTest() {
    @Inject lateinit var socketFactory: SocketDataChannelFactory

    class MockSocketWrapper : SocketDataChannel {
        var innerStatus: SocketDataChannel.SocketStatus =
            SocketDataChannel.SocketStatus.SOCKET_INITIALIZED

        var innerBound: Boolean = false

        override suspend fun initialize() {}

        override fun shutdown() {}

        override val status: SocketDataChannel.SocketStatus
            get() = innerStatus
        override var isBound: Boolean
            get() = innerBound
            set(value) {
                innerBound = value
            }

        override fun bind() {
            innerBound = true
        }

        override fun unbind() {
            innerBound = false
        }

        override var outputStream: OutputStream?
            get() = null
            set(_) {}

        override val isAvailable: Boolean
            get() = innerStatus == SOCKET_READY && !innerBound
    }
    @Primary
    @Singleton
    class MockSocketWrapperFactory : SocketDataChannelFactory {
        override fun makeSocket(socketFilePath: String): SocketDataChannel = MockSocketWrapper()
    }

    @Test
    fun test() {
        val socketDataChannelResourceHolder =
            SocketDataChannelResourceHolder(List<String>(10) { "" }, socketFactory)
        Assertions.assertNull(socketDataChannelResourceHolder.acquireSocketDataChannel())
        val m = socketDataChannelResourceHolder.sockets[0] as MockSocketWrapper
        m.innerStatus = SOCKET_READY
        assertNotNull(socketDataChannelResourceHolder.acquireSocketDataChannel())
        m.innerStatus = SocketDataChannel.SocketStatus.SOCKET_INITIALIZED
        Assertions.assertNull(socketDataChannelResourceHolder.acquireSocketDataChannel())
        m.innerStatus = SOCKET_READY
        m.innerBound = true
        Assertions.assertNull(socketDataChannelResourceHolder.acquireSocketDataChannel())
    }
}
