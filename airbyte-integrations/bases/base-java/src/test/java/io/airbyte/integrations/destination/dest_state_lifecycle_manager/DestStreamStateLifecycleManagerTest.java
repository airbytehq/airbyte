/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.LinkedList;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestStreamStateLifecycleManagerTest {

  private static final AirbyteMessage STREAM1_MESSAGE1 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("apples")).withStreamState(Jsons.jsonNode("a"))));
  private static final AirbyteMessage STREAM1_MESSAGE2 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("apples")).withStreamState(Jsons.jsonNode("b"))));
  private static final AirbyteMessage STREAM2_MESSAGE1 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(
              new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("bananas")).withStreamState(Jsons.jsonNode("10"))));

  private DestStreamStateLifecycleManager mgr;

  @BeforeEach
  void setup() {
    mgr = new DestStreamStateLifecycleManager();
  }

  /**
   * Demonstrates expected lifecycle of a state object for documentation purposes. Subsequent test get
   * into the details.
   */
  @Test
  void testBasicLifeCycle() {
    // starts with no state.
    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertTrue(mgr.listCommitted().isEmpty());

    mgr.addState(STREAM1_MESSAGE1);
    // new state supersedes previous ones. we should only see MESSAGE2 for STREAM1 from here on out.
    mgr.addState(STREAM1_MESSAGE2);
    // different stream, thus does not interact with messages from STREAM1.
    mgr.addState(STREAM2_MESSAGE1);

    // after adding a state, it is in pending only.
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)), mgr.listPending());
    assertTrue(mgr.listFlushed().isEmpty());
    assertTrue(mgr.listCommitted().isEmpty());

    mgr.markPendingAsFlushed();

    // after flushing the state it is in flushed only.
    assertTrue(mgr.listPending().isEmpty());
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)), mgr.listFlushed());
    assertTrue(mgr.listCommitted().isEmpty());

    // after committing the state it is in committed only.
    mgr.markFlushedAsCommitted();

    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)), mgr.listCommitted());
  }

  @Test
  void testPending() {
    mgr.addState(STREAM1_MESSAGE1);
    mgr.addState(STREAM1_MESSAGE2);
    mgr.addState(STREAM2_MESSAGE1);

    // verify the LAST message is returned.
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)), mgr.listPending());
    assertTrue(mgr.listFlushed().isEmpty());
    assertTrue(mgr.listCommitted().isEmpty());
  }

  /*
   * TODO: remove this test after all destination connectors have updated to reflect destination
   * checkpointing changes where flush/commit will be bundled into the same operation
   */
  @Deprecated
  @Test
  void testFlushed() {
    mgr.addState(STREAM1_MESSAGE1);
    mgr.addState(STREAM1_MESSAGE2);
    mgr.addState(STREAM2_MESSAGE1);
    mgr.markPendingAsFlushed();

    assertTrue(mgr.listPending().isEmpty());
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)), mgr.listFlushed());
    assertTrue(mgr.listCommitted().isEmpty());

    // verify that multiple calls to markPendingAsFlushed overwrite old states
    mgr.addState(STREAM1_MESSAGE1);
    mgr.markPendingAsFlushed();
    mgr.markPendingAsFlushed();

    assertTrue(mgr.listPending().isEmpty());
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE1, STREAM2_MESSAGE1)), mgr.listFlushed());
    assertTrue(mgr.listCommitted().isEmpty());
  }

  @Test
  void testCommitted() {
    mgr.addState(STREAM1_MESSAGE1);
    mgr.addState(STREAM1_MESSAGE2);
    mgr.addState(STREAM2_MESSAGE1);
    mgr.markPendingAsFlushed();
    mgr.markFlushedAsCommitted();

    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE2, STREAM2_MESSAGE1)), mgr.listCommitted());

    // verify that multiple calls to markFlushedAsCommitted overwrite old states
    mgr.addState(STREAM1_MESSAGE1);
    mgr.markPendingAsFlushed();
    mgr.markFlushedAsCommitted();
    mgr.markFlushedAsCommitted();

    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE1, STREAM2_MESSAGE1)), mgr.listCommitted());
  }

  /*
   * This section is to test for logic that is isolated to changes with respect to destination
   * checkpointing where it captures flush and commit are bundled into a transaction so
   *
   * buffer -(flush buffer)-> staging area -(copy into {staging_file})-> destination raw table
   */
  @Test
  void testPendingAsCommitted() {
    mgr.addState(STREAM1_MESSAGE1);
    mgr.markPendingAsCommitted();

    // verifies that we've skipped "Flushed" without needing to call `markPendingAsFlushed()` and
    // `markFlushedAsCommitted`
    assertTrue(mgr.listPending().isEmpty());
    assertEquals(new LinkedList<>(List.of(STREAM1_MESSAGE1)), mgr.listCommitted());
  }

}
