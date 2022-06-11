/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DestSingleStateLifecycleManagerTest {

  private static final AirbyteMessage MESSAGE1 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withStateType(AirbyteStateType.GLOBAL));
  private static final AirbyteMessage MESSAGE2 = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withStateType(AirbyteStateType.GLOBAL));

  private DestSingleStateLifecycleManager mgr;

  @BeforeEach
  void setup() {
    mgr = new DestSingleStateLifecycleManager();
  }

  @Test
  void testBasicLifeCycle() {
    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertTrue(mgr.listCommitted().isEmpty());

    mgr.addState(MESSAGE1);

    assertEquals(MESSAGE2, mgr.listPending().poll());
    assertTrue(mgr.listFlushed().isEmpty());
    assertTrue(mgr.listCommitted().isEmpty());

    mgr.markPendingAsFlushed();

    assertTrue(mgr.listPending().isEmpty());
    assertEquals(MESSAGE2, mgr.listFlushed().poll());
    assertTrue(mgr.listCommitted().isEmpty());

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
    // verify that multiple calls to markPendingAsFlushed work as expected.
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
    // verify that multiple calls to markFlushedAsCommitted work as expected overwrite with new records
    mgr.addState(MESSAGE1);
    mgr.markPendingAsFlushed();
    mgr.markFlushedAsCommitted();
    mgr.markFlushedAsCommitted();
    assertTrue(mgr.listPending().isEmpty());
    assertTrue(mgr.listFlushed().isEmpty());
    assertEquals(MESSAGE1, mgr.listCommitted().poll());
  }

}
