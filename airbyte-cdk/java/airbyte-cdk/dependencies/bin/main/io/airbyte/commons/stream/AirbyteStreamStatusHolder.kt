/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.stream

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor

/** Represents the current status of a stream provided by a source. */
class AirbyteStreamStatusHolder(
    private val airbyteStream: AirbyteStreamNameNamespacePair?,
    private val airbyteStreamStatus: AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
) {
    fun toTraceMessage(): AirbyteTraceMessage {
        val traceMessage = AirbyteTraceMessage()
        val streamStatusTraceMessage =
            AirbyteStreamStatusTraceMessage()
                .withStreamDescriptor(
                    StreamDescriptor()
                        .withName(airbyteStream!!.name)
                        .withNamespace(airbyteStream.namespace)
                )
                .withStatus(airbyteStreamStatus)
        return traceMessage
            .withEmittedAt(System.currentTimeMillis().toDouble())
            .withStreamStatus(streamStatusTraceMessage)
            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
    }
}
