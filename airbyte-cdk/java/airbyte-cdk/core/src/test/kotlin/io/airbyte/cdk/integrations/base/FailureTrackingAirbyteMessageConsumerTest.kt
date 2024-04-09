/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import io.airbyte.protocol.models.v0.AirbyteMessage
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.kotlin.any
import org.mockito.kotlin.mock

internal class FailureTrackingAirbyteMessageConsumerTest {
    @Test
    @Throws(Exception::class)
    fun testStartNoFailure() {
        val consumer = Mockito.spy(TestConsumer())
        consumer.start()
        consumer.close()

        Mockito.verify(consumer).close(false)
    }

    @Test
    @Throws(Exception::class)
    fun testStartWithFailure() {
        val consumer = Mockito.spy(TestConsumer())
        Mockito.doThrow(RuntimeException()).`when`(consumer).startTracked()

        // verify the exception still gets thrown.
        Assertions.assertThrows(RuntimeException::class.java) { consumer.start() }
        consumer.close()

        Mockito.verify(consumer).close(true)
    }

    @Test
    @Throws(Exception::class)
    fun testAcceptNoFailure() {
        val consumer = Mockito.spy(TestConsumer())

        val msg = Mockito.mock(AirbyteMessage::class.java)
        consumer.accept(msg)
        consumer.close()

        Mockito.verify(consumer).close(false)
    }

    @Test
    @Throws(Exception::class)
    fun testAcceptWithFailure() {
        val consumer = Mockito.spy(TestConsumer())
        val msg: AirbyteMessage = mock()
        Mockito.`when`(msg.type).thenReturn(AirbyteMessage.Type.RECORD)
        Mockito.doThrow(RuntimeException()).`when`(consumer).acceptTracked(any())

        // verify the exception still gets thrown.
        Assertions.assertThrows(RuntimeException::class.java) { consumer.accept(msg) }
        consumer.close()

        Mockito.verify(consumer).close(true)
    }

    internal class TestConsumer : FailureTrackingAirbyteMessageConsumer() {
        public override fun startTracked() {}

        public override fun acceptTracked(s: AirbyteMessage) {}

        public override fun close(hasFailed: Boolean) {}
    }
}
