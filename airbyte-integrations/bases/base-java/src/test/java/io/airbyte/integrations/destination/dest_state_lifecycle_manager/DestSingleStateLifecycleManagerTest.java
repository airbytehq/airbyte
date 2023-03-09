/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestSingleStateLifecycleManagerTest {

  private static final AirbyteMessage MESSAGE1 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withData(Jsons.jsonNode("a")));
  private static final AirbyteMessage MESSAGE2 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withData(Jsons.jsonNode("b")));

  private DestSingleStateLifecycleManager mgr;

  @BeforeEach
  void setup() {
    mgr = new DestSingleStateLifecycleManager();
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

    mgr.addState(MESSAGE1);
    // new state supersedes previous ones. we should only see MESSAGE2 from here on out.
    mgr.addState(MESSAGE2);

    // after adding a state, it is in pending only.
    assertEquals(MESSAGE2, mgr.listPending().poll());
    assertTrue(mgr.listFlushed().isEmpty());
    assertTrue(mgr.listCommitted().isEmpty());

    mgr.markPendingAsFlushed();

    // after flushing the state it is in flushed only.
    assertTrue(mgr.listPending().isEmpty());
    assertEquals(MESSAGE2, mgr.listFlushed().poll());
    assertTrue(mgr.listCommitted().isEmpty());

    // after committing the state it is in committed only.
    mgr.markFlushedAsCommitted();

    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertEquals(MESSAGE2, mgr.listCommitted().poll());
  }

  @Test
  void testPending() {
    mgr.addState(MESSAGE1);
    mgr.addState(MESSAGE2);

    // verify the LAST message is returned.
    assertEquals(MESSAGE2, mgr.listPending().poll());
    assertTrue(mgr.listFlushed().isEmpty());
    assertTrue(mgr.listCommitted().isEmpty());
  }

  @Test
  void testFlushed() {
    mgr.addState(MESSAGE1);
    mgr.addState(MESSAGE2);
    mgr.markPendingAsFlushed();

    assertTrue(mgr.listPending().isEmpty());
    assertEquals(MESSAGE2, mgr.listFlushed().poll());
    assertTrue(mgr.listCommitted().isEmpty());

    // verify that multiple calls to markPendingAsFlushed overwrite old states
    mgr.addState(MESSAGE1);
    mgr.markPendingAsFlushed();
    mgr.markPendingAsFlushed();

    assertTrue(mgr.listPending().isEmpty());
    assertEquals(MESSAGE1, mgr.listFlushed().poll());
    assertTrue(mgr.listCommitted().isEmpty());
  }

  @Test
  void testCommitted() {
    mgr.addState(MESSAGE1);
    mgr.addState(MESSAGE2);
    mgr.markPendingAsFlushed();
    mgr.markFlushedAsCommitted();

    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertEquals(MESSAGE2, mgr.listCommitted().poll());

    // verify that multiple calls to markFlushedAsCommitted overwrite old states
    mgr.addState(MESSAGE1);
    mgr.markPendingAsFlushed();
    mgr.markFlushedAsCommitted();
    mgr.markFlushedAsCommitted();

    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertEquals(MESSAGE1, mgr.listCommitted().poll());
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
  void testMarkPendingAsCommitted() {
    mgr.addState(MESSAGE1);
    mgr.addState(MESSAGE2);
    mgr.markPendingAsCommitted();

    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertEquals(MESSAGE2, mgr.listCommitted().poll());
  }

}
