/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.protocol.models.v0.*
import org.junit.Assert
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito
import java.time.Duration

class SourceStateIteratorTest {
    var mockProducer: SourceStateMessageProducer<*>? = null
    var messageIterator: Iterator<AirbyteMessage>? = null
    var stream: ConfiguredAirbyteStream? = null

    var sourceStateIterator: SourceStateIterator<*>? = null

    @BeforeEach
    fun setup() {
        mockProducer = Mockito.mock(SourceStateMessageProducer::class.java)
        stream = Mockito.mock(ConfiguredAirbyteStream::class.java)
        messageIterator = Mockito.mock<Iterator<*>>(MutableIterator::class.java)
        val stateEmitFrequency = StateEmitFrequency(1L, Duration.ofSeconds(100L))
        sourceStateIterator = SourceStateIterator<Any?>(messageIterator, stream, mockProducer, stateEmitFrequency)
    }

    // Provides a way to generate a record message and will verify corresponding spied functions have
    // been called.
    fun processRecordMessage() {
        Mockito.doReturn(true).`when`(messageIterator).hasNext()
        Mockito.doReturn(false).`when`(mockProducer).shouldEmitStateMessage(ArgumentMatchers.eq(stream))
        val message = AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(AirbyteRecordMessage())
        Mockito.doReturn(message).`when`(mockProducer).processRecordMessage(ArgumentMatchers.eq(stream), ArgumentMatchers.any<Any>())
        Mockito.doReturn(message).`when`(messageIterator).next()

        Assert.assertEquals(message, sourceStateIterator!!.computeNext())
        Mockito.verify(mockProducer, Mockito.atLeastOnce()).processRecordMessage(ArgumentMatchers.eq(stream), ArgumentMatchers.eq(message))
    }

    @Test
    fun testShouldProcessRecordMessage() {
        processRecordMessage()
    }

    @Test
    fun testShouldEmitStateMessage() {
        processRecordMessage()
        Mockito.doReturn(true).`when`(mockProducer).shouldEmitStateMessage(ArgumentMatchers.eq(stream))
        val stateMessage = AirbyteStateMessage()
        Mockito.doReturn(stateMessage).`when`(mockProducer).generateStateMessageAtCheckpoint(stream)
        val expectedMessage = AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
        expectedMessage.state.withSourceStats(AirbyteStateStats().withRecordCount(1.0))
        Assert.assertEquals(expectedMessage, sourceStateIterator!!.computeNext())
    }

    @Test
    fun testShouldEmitFinalStateMessage() {
        processRecordMessage()
        processRecordMessage()
        Mockito.doReturn(false).`when`(messageIterator).hasNext()
        val stateMessage = AirbyteStateMessage()
        Mockito.doReturn(stateMessage).`when`(mockProducer).createFinalStateMessage(stream)
        val expectedMessage = AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
        expectedMessage.state.withSourceStats(AirbyteStateStats().withRecordCount(2.0))
        Assert.assertEquals(expectedMessage, sourceStateIterator!!.computeNext())
    }

    @Test
    fun testShouldSendEndOfData() {
        processRecordMessage()
        Mockito.doReturn(false).`when`(messageIterator).hasNext()
        Mockito.doReturn(AirbyteStateMessage()).`when`(mockProducer).createFinalStateMessage(stream)
        sourceStateIterator!!.computeNext()

        // After sending the final state, if iterator was called again, we will return null.
        Assert.assertEquals(null, sourceStateIterator!!.computeNext())
    }

    @Test
    fun testShouldRethrowExceptions() {
        processRecordMessage()
        Mockito.doThrow(ArrayIndexOutOfBoundsException("unexpected error")).`when`(messageIterator).hasNext()
        Assert.assertThrows(RuntimeException::class.java) { sourceStateIterator!!.computeNext() }
    }
}
