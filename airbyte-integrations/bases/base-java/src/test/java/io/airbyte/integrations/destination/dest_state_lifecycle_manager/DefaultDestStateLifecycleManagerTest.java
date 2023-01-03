/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultDestStateLifecycleManagerTest {

  private static final AirbyteMessage UNSET_TYPE_MESSAGE = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage());
  private static final AirbyteMessage LEGACY_MESSAGE = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY));
  private static final AirbyteMessage GLOBAL_MESSAGE = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL));
  private static final AirbyteMessage STREAM_MESSAGE = new AirbyteMessage()
      .withType(Type.STATE)
      .withState(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("users"))));

  private DestStateLifecycleManager mgr1;
  private DestStateLifecycleManager singleStateMgr;
  private DestStateLifecycleManager streamMgr;

  @BeforeEach
  void setup() {
    singleStateMgr = mock(DestStateLifecycleManager.class);
    streamMgr = mock(DestStateLifecycleManager.class);
    mgr1 = new DefaultDestStateLifecycleManager(singleStateMgr, streamMgr);
  }

  @Test
  void testFailsOnIncompatibleStates() {
    final DefaultDestStateLifecycleManager manager1 = new DefaultDestStateLifecycleManager(singleStateMgr, streamMgr);
    manager1.addState(UNSET_TYPE_MESSAGE);
    manager1.addState(UNSET_TYPE_MESSAGE);
    manager1.addState(LEGACY_MESSAGE);
    assertThrows(IllegalArgumentException.class, () -> manager1.addState(GLOBAL_MESSAGE));
    assertThrows(IllegalArgumentException.class, () -> manager1.addState(STREAM_MESSAGE));

    final DefaultDestStateLifecycleManager manager2 = new DefaultDestStateLifecycleManager(singleStateMgr, streamMgr);
    manager2.addState(LEGACY_MESSAGE);
    manager2.addState(LEGACY_MESSAGE);
    manager2.addState(UNSET_TYPE_MESSAGE);
    assertThrows(IllegalArgumentException.class, () -> manager2.addState(GLOBAL_MESSAGE));
    assertThrows(IllegalArgumentException.class, () -> manager2.addState(STREAM_MESSAGE));

    final DefaultDestStateLifecycleManager manager3 = new DefaultDestStateLifecycleManager(singleStateMgr, streamMgr);
    manager3.addState(GLOBAL_MESSAGE);
    manager3.addState(GLOBAL_MESSAGE);
    assertThrows(IllegalArgumentException.class, () -> manager3.addState(UNSET_TYPE_MESSAGE));
    assertThrows(IllegalArgumentException.class, () -> manager3.addState(LEGACY_MESSAGE));
    assertThrows(IllegalArgumentException.class, () -> manager3.addState(STREAM_MESSAGE));

    final DefaultDestStateLifecycleManager manager4 = new DefaultDestStateLifecycleManager(singleStateMgr, streamMgr);
    manager4.addState(STREAM_MESSAGE);
    manager4.addState(STREAM_MESSAGE);
    assertThrows(IllegalArgumentException.class, () -> manager4.addState(UNSET_TYPE_MESSAGE));
    assertThrows(IllegalArgumentException.class, () -> manager4.addState(LEGACY_MESSAGE));
    assertThrows(IllegalArgumentException.class, () -> manager4.addState(GLOBAL_MESSAGE));
  }

  @Test
  void testDelegatesLegacyMessages() {
    mgr1.addState(UNSET_TYPE_MESSAGE);
    mgr1.addState(LEGACY_MESSAGE);
    mgr1.markPendingAsFlushed();
    mgr1.markFlushedAsCommitted();
    mgr1.listFlushed();
    mgr1.listCommitted();
    verify(singleStateMgr).addState(UNSET_TYPE_MESSAGE);
    verify(singleStateMgr).addState(LEGACY_MESSAGE);
    verify(singleStateMgr).markPendingAsFlushed();
    verify(singleStateMgr).markFlushedAsCommitted();
    verify(singleStateMgr).listFlushed();
    verify(singleStateMgr).listCommitted();
  }

  @Test
  void testDelegatesGlobalMessages() {
    mgr1.addState(GLOBAL_MESSAGE);
    mgr1.markPendingAsFlushed();
    mgr1.markFlushedAsCommitted();
    mgr1.listFlushed();
    mgr1.listCommitted();
    verify(singleStateMgr).addState(GLOBAL_MESSAGE);
    verify(singleStateMgr).markPendingAsFlushed();
    verify(singleStateMgr).markFlushedAsCommitted();
    verify(singleStateMgr).listFlushed();
    verify(singleStateMgr).listCommitted();
  }

  @Test
  void testDelegatesStreamMessages() {
    mgr1.addState(STREAM_MESSAGE);
    mgr1.markPendingAsFlushed();
    mgr1.markFlushedAsCommitted();
    mgr1.listFlushed();
    mgr1.listCommitted();

    verify(streamMgr).addState(STREAM_MESSAGE);
    verify(streamMgr).markPendingAsFlushed();
    verify(streamMgr).markFlushedAsCommitted();
    verify(streamMgr).listFlushed();
    verify(streamMgr).listCommitted();
  }

}
