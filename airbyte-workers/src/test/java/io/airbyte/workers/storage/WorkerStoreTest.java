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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

class WorkerStoreTest {

  private static final UUID ID = UUID.randomUUID();
  private static final JsonNode DOCUMENT = Jsons.jsonNode(ImmutableMap.of("a", 1));

  private DocumentStoreClient documentStore;
  private WorkerStore store;

  @BeforeEach
  void setup() {
    documentStore = mock(DocumentStoreClient.class);
    store = new WorkerStore(documentStore);
  }

  @Test
  void testWrite() {
    store.set(ID, DOCUMENT);
    // overwrites are allowed, so test calling it twice.
    store.set(ID, DOCUMENT);
    verify(documentStore, times(2)).write(ID.toString(), Jsons.serialize(DOCUMENT));
  }

  @Test
  void testReadExists() {
    when(documentStore.read(ID.toString())).thenReturn(Optional.of(Jsons.serialize(DOCUMENT)));
    assertEquals(Optional.of(DOCUMENT), store.get(ID));
  }

  @Test
  void testReadNotExists() {
    when(documentStore.read(ID.toString())).thenReturn(Optional.empty());
    assertEquals(Optional.empty(), store.get(ID));
  }

  @Test
  void testDeleteExists() {
    when(documentStore.delete(ID.toString())).thenReturn(true);
    assertTrue(store.delete(ID));
  }

  @Test
  void testDeleteNotExists() {
    when(documentStore.delete(ID.toString())).thenReturn(false);
    assertFalse(store.delete(ID));
  }

}
