/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage

class DestinationUncleanExitException(
    exitCode: Int,
    traceMessages: List<AirbyteErrorTraceMessage>
) :
    Exception(
        """
        Destination process exited uncleanly: $exitCode
        Trace messages:
        """.trimIndent()
        // explicit concat because otherwise trimIndent behaves badly
        + traceMessages
    ) {
    companion object {
        // generic type erasure strikes again >.>
        // this can't just be a second constructor, because both constructors
        // would have signature `traceMessages: List`.
        // so we have to pull this into a companion object function.
        fun of(exitCode: Int, traceMessages: List<AirbyteTraceMessage>) =
            DestinationUncleanExitException(
                exitCode,
                traceMessages.filter { it.type == AirbyteTraceMessage.Type.ERROR }.map { it.error }
            )
    }
}
