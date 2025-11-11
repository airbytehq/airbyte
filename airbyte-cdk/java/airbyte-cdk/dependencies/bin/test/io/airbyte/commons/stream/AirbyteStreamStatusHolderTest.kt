/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.stream

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Test suite for the [AirbyteStreamStatusHolder] class. */
internal class AirbyteStreamStatusHolderTest {
    @Test
    fun testToTraceMessage() {
        val startTime = System.currentTimeMillis().toDouble()
        val airbyteStreamNameAndNamespacePair = AirbyteStreamNameNamespacePair("name", "namespace")
        val streamStatus = AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.RUNNING
        val holder = AirbyteStreamStatusHolder(airbyteStreamNameAndNamespacePair, streamStatus)

        val traceMessage = holder.toTraceMessage()
        Assertions.assertTrue(traceMessage.emittedAt >= startTime)
        Assertions.assertEquals(AirbyteTraceMessage.Type.STREAM_STATUS, traceMessage.type)
        Assertions.assertEquals(streamStatus, traceMessage.streamStatus.status)
        Assertions.assertEquals(
            StreamDescriptor()
                .withName(airbyteStreamNameAndNamespacePair.name)
                .withNamespace(airbyteStreamNameAndNamespacePair.namespace),
            traceMessage.streamStatus.streamDescriptor
        )
    }

    @Test
    fun testToTraceMessageWithOptionalData() {
        val startTime = System.currentTimeMillis().toDouble()
        val airbyteStreamNameAndNamespacePair = AirbyteStreamNameNamespacePair("name", "namespace")
        val streamStatus = AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
        val holder = AirbyteStreamStatusHolder(airbyteStreamNameAndNamespacePair, streamStatus)

        val traceMessage = holder.toTraceMessage()
        Assertions.assertTrue(traceMessage.emittedAt >= startTime)
        Assertions.assertEquals(AirbyteTraceMessage.Type.STREAM_STATUS, traceMessage.type)
        Assertions.assertEquals(streamStatus, traceMessage.streamStatus.status)
        Assertions.assertEquals(
            StreamDescriptor()
                .withName(airbyteStreamNameAndNamespacePair.name)
                .withNamespace(airbyteStreamNameAndNamespacePair.namespace),
            traceMessage.streamStatus.streamDescriptor
        )
    }
}
