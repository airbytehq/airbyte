/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.airbyte.cdk.integrations.debezium.CdcStateHandler
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import java.util.*
import org.junit.Assert
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito
import org.mockito.kotlin.any
import org.mockito.kotlin.eq
import org.mockito.kotlin.mock

class DebeziumMessageProducerTest {
    private var producer: DebeziumMessageProducer<*>? = null

    var cdcStateHandler: CdcStateHandler = mock()
    var targetPosition: CdcTargetPosition<Any> = mock()
    var eventConverter: DebeziumEventConverter = mock()
    var offsetManager: AirbyteFileOffsetBackingStore = mock()
    var schemaHistoryManager: AirbyteSchemaHistoryStorage = mock()

    @BeforeEach
    fun setUp() {
        cdcStateHandler = Mockito.mock(CdcStateHandler::class.java)
        Mockito.`when`(cdcStateHandler.isCdcCheckpointEnabled).thenReturn(true)
        targetPosition = mock()
        eventConverter = Mockito.mock(DebeziumEventConverter::class.java)
        offsetManager = Mockito.mock(AirbyteFileOffsetBackingStore::class.java)
        Mockito.`when`<Map<String, String>>(offsetManager.read()).thenReturn(OFFSET_MANAGER_READ)
        schemaHistoryManager = Mockito.mock(AirbyteSchemaHistoryStorage::class.java)
        Mockito.`when`(schemaHistoryManager.read()).thenReturn(SCHEMA)
        producer =
            DebeziumMessageProducer<Any>(
                cdcStateHandler,
                targetPosition,
                eventConverter,
                offsetManager,
                Optional.of(schemaHistoryManager)
            )
    }

    @Test
    fun testProcessRecordMessage() {
        val message = Mockito.mock(ChangeEventWithMetadata::class.java)

        Mockito.`when`(targetPosition.isSameOffset(any(), any())).thenReturn(true)
        producer!!.processRecordMessage(null, message)
        Mockito.verify(eventConverter).toAirbyteMessage(message)
        Assert.assertFalse(producer!!.shouldEmitStateMessage(null))
    }

    @Test
    fun testProcessRecordMessageWithStateMessage() {
        val message = Mockito.mock(ChangeEventWithMetadata::class.java)

        Mockito.`when`(targetPosition.isSameOffset(any(), any())).thenReturn(false)
        Mockito.`when`(targetPosition.isEventAheadOffset(OFFSET_MANAGER_READ, message))
            .thenReturn(true)
        producer!!.processRecordMessage(null, message)
        Mockito.verify(eventConverter).toAirbyteMessage(message)
        Assert.assertTrue(producer!!.shouldEmitStateMessage(null))

        Mockito.`when`(cdcStateHandler.isCdcCheckpointEnabled).thenReturn(false)
        Mockito.`when`(cdcStateHandler.saveState(eq(OFFSET_MANAGER_READ), eq(SCHEMA)))
            .thenReturn(AirbyteMessage().withState(STATE_MESSAGE))

        Assert.assertEquals(producer!!.generateStateMessageAtCheckpoint(null), STATE_MESSAGE)
    }

    @Test
    fun testGenerateFinalMessageNoProgress() {
        Mockito.`when`(cdcStateHandler.saveState(eq(OFFSET_MANAGER_READ), eq(SCHEMA)))
            .thenReturn(AirbyteMessage().withState(STATE_MESSAGE))

        // initialOffset will be OFFSET_MANAGER_READ, final state would be OFFSET_MANAGER_READ2.
        // Mock CDC handler will only accept OFFSET_MANAGER_READ.
        Mockito.`when`<Map<String, String>>(offsetManager.read()).thenReturn(OFFSET_MANAGER_READ2)

        Mockito.`when`(targetPosition.isSameOffset(OFFSET_MANAGER_READ, OFFSET_MANAGER_READ2))
            .thenReturn(true)

        Assert.assertEquals(producer!!.createFinalStateMessage(null), STATE_MESSAGE)
    }

    @Test
    fun testGenerateFinalMessageWithProgress() {
        Mockito.`when`(cdcStateHandler.saveState(eq(OFFSET_MANAGER_READ2), eq(SCHEMA)))
            .thenReturn(AirbyteMessage().withState(STATE_MESSAGE))

        // initialOffset will be OFFSET_MANAGER_READ, final state would be OFFSET_MANAGER_READ2.
        // Mock CDC handler will only accept OFFSET_MANAGER_READ2.
        Mockito.`when`<Map<String, String>>(offsetManager.read()).thenReturn(OFFSET_MANAGER_READ2)
        Mockito.`when`(targetPosition.isSameOffset(OFFSET_MANAGER_READ, OFFSET_MANAGER_READ2))
            .thenReturn(false)

        Assert.assertEquals(producer!!.createFinalStateMessage(null), STATE_MESSAGE)
    }

    companion object {
        private val OFFSET_MANAGER_READ: Map<String, String> =
            HashMap(java.util.Map.of("key", "value"))
        private val OFFSET_MANAGER_READ2: Map<String, String> =
            HashMap(java.util.Map.of("key2", "value2"))

        private val SCHEMA: AirbyteSchemaHistoryStorage.SchemaHistory<String> =
            AirbyteSchemaHistoryStorage.SchemaHistory("schema", false)

        private val STATE_MESSAGE: AirbyteStateMessage =
            AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
    }
}
