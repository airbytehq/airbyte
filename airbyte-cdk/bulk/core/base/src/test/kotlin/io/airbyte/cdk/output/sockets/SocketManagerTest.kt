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
class SocketManagerTest(private val socketManager: SocketManager) {
//    @Inject lateinit var socketManager: SocketManager
    @Inject lateinit var socketFactory: SocketWrapperFactory
    class MockSocketWrapper(
    ) : SocketWrapper {
        override suspend fun initializeSocket() {
        }

        override suspend fun closeSocket() {
        }

        var innerStatus: SocketWrapper.SocketStatus = SocketWrapper.SocketStatus.SOCKET_INITIALIZED
        var innerBound: Boolean = false
        override val status: SocketWrapper.SocketStatus
            get() = innerStatus
        override var bound: Boolean
            get() = innerBound
            set(value: Boolean) { innerBound = value }

    }
    @Primary
    @Singleton
    class MockSocketWrapperFactory: SocketWrapperFactory {
        override fun makeSocket(socketFilePath: String): SocketWrapper =
            MockSocketWrapper()

    }

    @Test
    fun test() {
        val socketManager: SocketManager = SocketManager(List<String>(10) {""}, socketFactory)
        assertNull(socketManager.getFree())
        val m = socketManager.sockets[0] as MockSocketWrapper
        m.innerStatus = SocketWrapper.SocketStatus.SOCKET_READY
        assertNotNull(socketManager.getFree())
        m.innerStatus = SocketWrapper.SocketStatus.SOCKET_INITIALIZED
        assertNull(socketManager.getFree())
        m.innerStatus = SocketWrapper.SocketStatus.SOCKET_READY
        m.innerBound = true
        assertNull(socketManager.getFree())
    }
}
