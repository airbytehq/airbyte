/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class DestSingleStateLifecycleManagerTest {
    private var mgr: DestSingleStateLifecycleManager? = null

    @BeforeEach
    fun setup() {
        mgr = DestSingleStateLifecycleManager()
    }

    /**
     * Demonstrates expected lifecycle of a state object for documentation purposes. Subsequent test
     * get into the details.
     */
    @Test
    fun testBasicLifeCycle() {
        // starts with no state.
        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())

        mgr!!.addState(MESSAGE1)
        // new state supersedes previous ones. we should only see MESSAGE2 from here on out.
        mgr!!.addState(MESSAGE2)

        // after adding a state, it is in pending only.
        Assertions.assertEquals(MESSAGE2, mgr!!.listPending().poll())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())

        mgr!!.markPendingAsFlushed()

        // after flushing the state it is in flushed only.
        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertEquals(MESSAGE2, mgr!!.listFlushed().poll())
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())

        // after committing the state it is in committed only.
        mgr!!.markFlushedAsCommitted()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertEquals(MESSAGE2, mgr!!.listCommitted().poll())
    }

    @Test
    fun testPending() {
        mgr!!.addState(MESSAGE1)
        mgr!!.addState(MESSAGE2)

        // verify the LAST message is returned.
        Assertions.assertEquals(MESSAGE2, mgr!!.listPending().poll())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())
    }

    @Test
    fun testFlushed() {
        mgr!!.addState(MESSAGE1)
        mgr!!.addState(MESSAGE2)
        mgr!!.markPendingAsFlushed()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertEquals(MESSAGE2, mgr!!.listFlushed().poll())
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())

        // verify that multiple calls to markPendingAsFlushed overwrite old states
        mgr!!.addState(MESSAGE1)
        mgr!!.markPendingAsFlushed()
        mgr!!.markPendingAsFlushed()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertEquals(MESSAGE1, mgr!!.listFlushed().poll())
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())
    }

    @Test
    fun testCommitted() {
        mgr!!.addState(MESSAGE1)
        mgr!!.addState(MESSAGE2)
        mgr!!.markPendingAsFlushed()
        mgr!!.markFlushedAsCommitted()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertEquals(MESSAGE2, mgr!!.listCommitted().poll())

        // verify that multiple calls to markFlushedAsCommitted overwrite old states
        mgr!!.addState(MESSAGE1)
        mgr!!.markPendingAsFlushed()
        mgr!!.markFlushedAsCommitted()
        mgr!!.markFlushedAsCommitted()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertEquals(MESSAGE1, mgr!!.listCommitted().poll())
    }

    /*
     * This change follows the same changes in DestStreamStateLifecycleManager where the goal is to
     * confirm that `markPendingAsCommitted` combines what was previous `markPendingAsFlushed` and
     * `markFlushedAsCommitted`
     *
     * The reason for this method is due to destination checkpointing will no longer hold into a state
     * as "Flushed" but immediately commit records to the destination's final table
     */
    @Test
    fun testMarkPendingAsCommitted() {
        mgr!!.addState(MESSAGE1)
        mgr!!.addState(MESSAGE2)
        mgr!!.markPendingAsCommitted()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertEquals(MESSAGE2, mgr!!.listCommitted().poll())
    }

    companion object {
        private val MESSAGE1: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withData(Jsons.jsonNode("a"))
                )
        private val MESSAGE2: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                        .withData(Jsons.jsonNode("b"))
                )
    }
}
