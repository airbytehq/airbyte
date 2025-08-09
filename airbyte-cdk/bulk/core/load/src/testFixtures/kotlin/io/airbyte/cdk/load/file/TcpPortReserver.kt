/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import java.net.ServerSocket

/** Reserves a unique unused port for testing. */
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
