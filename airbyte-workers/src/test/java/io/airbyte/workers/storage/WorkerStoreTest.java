/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class WorkerStoreTest {

  private static final UUID ACTIVITY_RUN_ID = UUID.randomUUID();
  private static final State STATE = new State().withState(Jsons.jsonNode(ImmutableMap.of("a", 1)));

  private DocumentStoreClient documentStore;
  private WorkerStore store;

  @BeforeEach
  void setup() {
    documentStore = mock(DocumentStoreClient.class);
    store = new WorkerStore(documentStore);
  }

  @Test
  void testWrite() {
    store.setState(ACTIVITY_RUN_ID, STATE);
    // overwrites are allowed, so test calling it twice.
    store.setState(ACTIVITY_RUN_ID, STATE);
    verify(documentStore, times(2)).write(ACTIVITY_RUN_ID.toString(), Jsons.serialize(STATE));
  }

  @Test
  void testReadExists() {
    when(documentStore.read(ACTIVITY_RUN_ID.toString())).thenReturn(Optional.of(Jsons.serialize(STATE)));
    assertEquals(Optional.of(STATE), store.getState(ACTIVITY_RUN_ID));
  }

  @Test
  void testReadNotExists() {
    when(documentStore.read(ACTIVITY_RUN_ID.toString())).thenReturn(Optional.empty());
    assertEquals(Optional.empty(), store.getState(ACTIVITY_RUN_ID));
  }

  @Test
  void testDeleteExists() {
    when(documentStore.delete(ACTIVITY_RUN_ID.toString())).thenReturn(true);
    assertTrue(store.deleteState(ACTIVITY_RUN_ID));
  }

  @Test
  void testDeleteNotExists() {
    when(documentStore.delete(ACTIVITY_RUN_ID.toString())).thenReturn(false);
    assertFalse(store.deleteState(ACTIVITY_RUN_ID));
  }

}
