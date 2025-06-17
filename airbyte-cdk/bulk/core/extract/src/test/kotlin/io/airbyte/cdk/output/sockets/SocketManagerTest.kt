package io.airbyte.cdk.output.sockets

import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.PropertySource
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

@MicronautTest
@PropertySource(
    value =
        [
            Property(name = SPEED_MODE_PROPERTY, value = "boosted"),
        ]
)
class SocketManagerTest(private val socketDataChannelHolder: SocketDataChannelHolder) {
//    @Inject lateinit var socketManager: SocketManager
    @Inject lateinit var socketFactory: SocketDataChannelFactory
    class MockSocketWrapper(
    ) : SocketDataChannel {
        override suspend fun initializeSocket() {
        }

        override suspend fun shutdownSocket() {
        }

        var innerStatus: SocketDataChannel.SocketStatus = SocketDataChannel.SocketStatus.SOCKET_INITIALIZED
        var innerBound: Boolean = false
        override val status: SocketDataChannel.SocketStatus
            get() = innerStatus
        override var bound: Boolean
            get() = innerBound
            set(value: Boolean) { innerBound = value }

        override fun bindSocket() {
            innerBound = true
        }

        override fun unbindSocket() {
            innerBound = false
        }

    }
    @Primary
    @Singleton
    class MockSocketWrapperFactory: SocketDataChannelFactory {
        override fun makeSocket(socketFilePath: String): SocketDataChannel =
            MockSocketWrapper()

    }

    @Test
    fun test() {
        val socketDataChannelHolder: SocketDataChannelHolder = SocketDataChannelHolder(List<String>(10) {""}, socketFactory)
        assertNull(socketDataChannelHolder.bindFreeSocket())
        val m = socketDataChannelHolder.sockets[0] as MockSocketWrapper
        m.innerStatus = SocketDataChannel.SocketStatus.SOCKET_READY
        assertNotNull(socketDataChannelHolder.bindFreeSocket())
        m.innerStatus = SocketDataChannel.SocketStatus.SOCKET_INITIALIZED
        assertNull(socketDataChannelHolder.bindFreeSocket())
        m.innerStatus = SocketDataChannel.SocketStatus.SOCKET_READY
        m.innerBound = true
        assertNull(socketDataChannelHolder.bindFreeSocket())
    }
}
