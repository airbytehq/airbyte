/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.message.CheckpointMessage
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class StateStoreTest {
    @Test
    fun `test accept and remove`() {
        val stateStore = StateStore()
        val key = StateKey(1, listOf("partition1"))
        val message = mockk<CheckpointMessage>()

        stateStore.accept(key, message)
        assertEquals(1, stateStore.states.size)

        val removedMessage = stateStore.remove(key)
        assertNotNull(removedMessage)
        assertSame(message, removedMessage)
        assertTrue(stateStore.states.isEmpty())
    }
}
