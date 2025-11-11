/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class DefaultDestStateLifecycleManagerTest {
    private lateinit var mgr1: DestStateLifecycleManager
    private lateinit var singleStateMgr: DestStateLifecycleManager
    private lateinit var streamMgr: DestStateLifecycleManager

    @BeforeEach
    fun setup() {
        singleStateMgr = Mockito.mock(DestStateLifecycleManager::class.java)
        streamMgr = Mockito.mock(DestStateLifecycleManager::class.java)
        mgr1 = DefaultDestStateLifecycleManager(singleStateMgr, streamMgr)
    }

    @Test
    fun testFailsOnIncompatibleStates() {
        val manager1 = DefaultDestStateLifecycleManager(singleStateMgr, streamMgr)
        manager1.addState(UNSET_TYPE_MESSAGE)
        manager1.addState(UNSET_TYPE_MESSAGE)
        manager1.addState(LEGACY_MESSAGE)
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager1.addState(GLOBAL_MESSAGE)
        }
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager1.addState(STREAM_MESSAGE)
        }

        val manager2 = DefaultDestStateLifecycleManager(singleStateMgr, streamMgr)
        manager2.addState(LEGACY_MESSAGE)
        manager2.addState(LEGACY_MESSAGE)
        manager2.addState(UNSET_TYPE_MESSAGE)
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager2.addState(GLOBAL_MESSAGE)
        }
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager2.addState(STREAM_MESSAGE)
        }

        val manager3 = DefaultDestStateLifecycleManager(singleStateMgr, streamMgr)
        manager3.addState(GLOBAL_MESSAGE)
        manager3.addState(GLOBAL_MESSAGE)
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager3.addState(UNSET_TYPE_MESSAGE)
        }
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager3.addState(LEGACY_MESSAGE)
        }
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager3.addState(STREAM_MESSAGE)
        }

        val manager4 = DefaultDestStateLifecycleManager(singleStateMgr, streamMgr)
        manager4.addState(STREAM_MESSAGE)
        manager4.addState(STREAM_MESSAGE)
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager4.addState(UNSET_TYPE_MESSAGE)
        }
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager4.addState(LEGACY_MESSAGE)
        }
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            manager4.addState(GLOBAL_MESSAGE)
        }
    }

    @Test
    fun testDelegatesLegacyMessages() {
        mgr1.addState(UNSET_TYPE_MESSAGE)
        mgr1.addState(LEGACY_MESSAGE)
        mgr1.markPendingAsFlushed()
        mgr1.markFlushedAsCommitted()
        mgr1.listFlushed()
        mgr1.listCommitted()
        Mockito.verify(singleStateMgr).addState(UNSET_TYPE_MESSAGE)
        Mockito.verify(singleStateMgr).addState(LEGACY_MESSAGE)
        Mockito.verify(singleStateMgr).markPendingAsFlushed()
        Mockito.verify(singleStateMgr).markFlushedAsCommitted()
        Mockito.verify(singleStateMgr).listFlushed()
        Mockito.verify(singleStateMgr).listCommitted()
    }

    @Test
    fun testDelegatesGlobalMessages() {
        mgr1.addState(GLOBAL_MESSAGE)
        mgr1.markPendingAsFlushed()
        mgr1.markFlushedAsCommitted()
        mgr1.listFlushed()
        mgr1.listCommitted()
        Mockito.verify(singleStateMgr).addState(GLOBAL_MESSAGE)
        Mockito.verify(singleStateMgr).markPendingAsFlushed()
        Mockito.verify(singleStateMgr).markFlushedAsCommitted()
        Mockito.verify(singleStateMgr).listFlushed()
        Mockito.verify(singleStateMgr).listCommitted()
    }

    @Test
    fun testDelegatesStreamMessages() {
        mgr1.addState(STREAM_MESSAGE)
        mgr1.markPendingAsFlushed()
        mgr1.markFlushedAsCommitted()
        mgr1.listFlushed()
        mgr1.listCommitted()

        Mockito.verify(streamMgr).addState(STREAM_MESSAGE)
        Mockito.verify(streamMgr).markPendingAsFlushed()
        Mockito.verify(streamMgr).markFlushedAsCommitted()
        Mockito.verify(streamMgr).listFlushed()
        Mockito.verify(streamMgr).listCommitted()
    }

    companion object {
        private val UNSET_TYPE_MESSAGE: AirbyteMessage =
            AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(AirbyteStateMessage())
        private val LEGACY_MESSAGE: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                )
        private val GLOBAL_MESSAGE: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                )
        private val STREAM_MESSAGE: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(StreamDescriptor().withName("users"))
                        )
                )
    }
}
