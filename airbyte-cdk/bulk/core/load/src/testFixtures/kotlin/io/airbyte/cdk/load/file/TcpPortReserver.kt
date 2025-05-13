package io.airbyte.cdk.load.file

import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.mina.util.ConcurrentHashSet
import java.net.ServerSocket
import java.util.concurrent.ConcurrentHashMap

/**
 * Reserves a unique unused port for testing.
 */
class TcpPortReserver {
    companion object {
        fun findAvailablePort(): Int {
            while (true) {
               ServerSocket(/* port = */ 0).use { socket ->
                   return socket.localPort
                }
            }
        }
    }
}
