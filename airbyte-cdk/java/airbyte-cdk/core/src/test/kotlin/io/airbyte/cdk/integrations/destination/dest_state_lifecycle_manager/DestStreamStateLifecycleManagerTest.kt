/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.*
import java.util.List
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class DestStreamStateLifecycleManagerTest {
    private var mgr: DestStreamStateLifecycleManager? = null

    @BeforeEach
    fun setup() {
        mgr = DestStreamStateLifecycleManager("default_namespace")
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

        mgr!!.addState(STREAM1_MESSAGE1)
        // new state supersedes previous ones. we should only see MESSAGE2 for STREAM1 from here on
        // out.
        mgr!!.addState(STREAM1_MESSAGE2)
        // different stream, thus does not interact with messages from STREAM1.
        mgr!!.addState(STREAM2_MESSAGE1)

        // after adding a state, it is in pending only.
        Assertions.assertEquals(
            LinkedList(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)),
            mgr!!.listPending()
        )
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())

        mgr!!.markPendingAsFlushed()

        // after flushing the state it is in flushed only.
        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertEquals(
            LinkedList(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)),
            mgr!!.listFlushed()
        )
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())

        // after committing the state it is in committed only.
        mgr!!.markFlushedAsCommitted()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertEquals(
            LinkedList(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)),
            mgr!!.listCommitted()
        )
    }

    @Test
    fun testPending() {
        mgr!!.addState(STREAM1_MESSAGE1)
        mgr!!.addState(STREAM1_MESSAGE2)
        mgr!!.addState(STREAM2_MESSAGE1)

        // verify the LAST message is returned.
        Assertions.assertEquals(
            LinkedList(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)),
            mgr!!.listPending()
        )
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())
    }

    /*
     * TODO: remove this test after all destination connectors have updated to reflect destination
     * checkpointing changes where flush/commit will be bundled into the same operation
     */
    @Deprecated("")
    @Test
    fun testFlushed() {
        mgr!!.addState(STREAM1_MESSAGE1)
        mgr!!.addState(STREAM1_MESSAGE2)
        mgr!!.addState(STREAM2_MESSAGE1)
        mgr!!.markPendingAsFlushed()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertEquals(
            LinkedList(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)),
            mgr!!.listFlushed()
        )
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())

        // verify that multiple calls to markPendingAsFlushed overwrite old states
        mgr!!.addState(STREAM1_MESSAGE1)
        mgr!!.markPendingAsFlushed()
        mgr!!.markPendingAsFlushed()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertEquals(
            LinkedList(List.of(STREAM1_MESSAGE1, STREAM2_MESSAGE1)),
            mgr!!.listFlushed()
        )
        Assertions.assertTrue(mgr!!.listCommitted().isEmpty())
    }

    @Test
    fun testCommitted() {
        mgr!!.addState(STREAM1_MESSAGE1)
        mgr!!.addState(STREAM1_MESSAGE2)
        mgr!!.addState(STREAM2_MESSAGE1)
        mgr!!.markPendingAsFlushed()
        mgr!!.markFlushedAsCommitted()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertEquals(
            LinkedList(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)),
            mgr!!.listCommitted()
        )

        // verify that multiple calls to markFlushedAsCommitted overwrite old states
        mgr!!.addState(STREAM1_MESSAGE1)
        mgr!!.markPendingAsFlushed()
        mgr!!.markFlushedAsCommitted()
        mgr!!.markFlushedAsCommitted()

        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertTrue(mgr!!.listFlushed().isEmpty())
        Assertions.assertEquals(
            LinkedList(List.of(STREAM1_MESSAGE1, STREAM2_MESSAGE1)),
            mgr!!.listCommitted()
        )
    }

    /*
     * This section is to test for logic that is isolated to changes with respect to destination
     * checkpointing where it captures flush and commit are bundled into a transaction so
     *
     * buffer -(flush buffer)-> staging area -(copy into {staging_file})-> destination raw table
     */
    @Test
    fun testPendingAsCommitted() {
        mgr!!.addState(STREAM1_MESSAGE1)
        mgr!!.markPendingAsCommitted()

        // verifies that we've skipped "Flushed" without needing to call `markPendingAsFlushed()`
        // and
        // `markFlushedAsCommitted`
        Assertions.assertTrue(mgr!!.listPending().isEmpty())
        Assertions.assertEquals(LinkedList(List.of(STREAM1_MESSAGE1)), mgr!!.listCommitted())
    }

    companion object {
        private val STREAM1_MESSAGE1: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(StreamDescriptor().withName("apples"))
                                .withStreamState(Jsons.jsonNode("a"))
                        )
                )
        private val STREAM1_MESSAGE2: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(StreamDescriptor().withName("apples"))
                                .withStreamState(Jsons.jsonNode("b"))
                        )
                )
        private val STREAM2_MESSAGE1: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.STATE)
                .withState(
                    AirbyteStateMessage()
                        .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                        .withStream(
                            AirbyteStreamState()
                                .withStreamDescriptor(StreamDescriptor().withName("bananas"))
                                .withStreamState(Jsons.jsonNode("10"))
                        )
                )
    }
}
