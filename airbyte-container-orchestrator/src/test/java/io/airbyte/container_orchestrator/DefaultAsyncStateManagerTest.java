/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;
import static org.mockito.Mockito.when;

import io.airbyte.workers.general.DocumentStoreClient;
import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.KubePodInfo;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultAsyncStateManagerTest {

  private static final KubePodInfo KUBE_POD_INFO = new KubePodInfo("default", "pod1");
  private static final String OUTPUT = "some output value";

  private DocumentStoreClient documentStore;
  private AsyncStateManager stateManager;

  @BeforeEach
  void setup() {
    documentStore = mock(DocumentStoreClient.class);
    stateManager = new DefaultAsyncStateManager(documentStore);
  }

  @Test
  void testEmptyWrite() {
    stateManager.write(KUBE_POD_INFO, AsyncKubePodStatus.INITIALIZING);

    // test for overwrite (which should be allowed)
    stateManager.write(KUBE_POD_INFO, AsyncKubePodStatus.INITIALIZING);

    final var key = getKey(AsyncKubePodStatus.INITIALIZING);
    verify(documentStore, times(2)).write(key, "");
  }

  @Test
  void testContentfulWrite() {
    stateManager.write(KUBE_POD_INFO, AsyncKubePodStatus.SUCCEEDED, OUTPUT);

    final var key = getKey(AsyncKubePodStatus.SUCCEEDED);
    verify(documentStore, times(1)).write(key, OUTPUT);
  }

  @Test
  void testReadingOutputWhenItExists() {
    final var key = getKey(AsyncKubePodStatus.SUCCEEDED);
    when(documentStore.read(key)).thenReturn(Optional.of(OUTPUT));
    assertEquals(OUTPUT, stateManager.getOutput(KUBE_POD_INFO));
  }

  @Test
  void testReadingOutputWhenItDoesNotExist() {
    // getting the output should throw an exception when there is no record in the document store
    assertThrows(IllegalArgumentException.class, () -> {
      stateManager.getOutput(KUBE_POD_INFO);
    });
  }

  @Test
  void testSuccessfulStatusRetrievalLifecycle() {
    when(documentStore.read(getKey(AsyncKubePodStatus.INITIALIZING))).thenReturn(Optional.empty());
    final var beforeInitializingStatus = stateManager.getStatus(KUBE_POD_INFO);
    assertEquals(AsyncKubePodStatus.NOT_STARTED, beforeInitializingStatus);

    when(documentStore.read(getKey(AsyncKubePodStatus.INITIALIZING))).thenReturn(Optional.of(""));
    final var initializingStatus = stateManager.getStatus(KUBE_POD_INFO);
    assertEquals(AsyncKubePodStatus.INITIALIZING, initializingStatus);

    when(documentStore.read(getKey(AsyncKubePodStatus.RUNNING))).thenReturn(Optional.of(""));
    final var runningStatus = stateManager.getStatus(KUBE_POD_INFO);
    assertEquals(AsyncKubePodStatus.RUNNING, runningStatus);

    when(documentStore.read(getKey(AsyncKubePodStatus.SUCCEEDED))).thenReturn(Optional.of("output"));
    final var succeededStatus = stateManager.getStatus(KUBE_POD_INFO);
    assertEquals(AsyncKubePodStatus.SUCCEEDED, succeededStatus);
  }

  @Test
  void testFailureStatusRetrievalLifecycle() {
    when(documentStore.read(getKey(AsyncKubePodStatus.INITIALIZING))).thenReturn(Optional.empty());
    final var beforeInitializingStatus = stateManager.getStatus(KUBE_POD_INFO);
    assertEquals(AsyncKubePodStatus.NOT_STARTED, beforeInitializingStatus);

    when(documentStore.read(getKey(AsyncKubePodStatus.INITIALIZING))).thenReturn(Optional.of(""));
    final var initializingStatus = stateManager.getStatus(KUBE_POD_INFO);
    assertEquals(AsyncKubePodStatus.INITIALIZING, initializingStatus);

    when(documentStore.read(getKey(AsyncKubePodStatus.RUNNING))).thenReturn(Optional.of(""));
    final var runningStatus = stateManager.getStatus(KUBE_POD_INFO);
    assertEquals(AsyncKubePodStatus.RUNNING, runningStatus);

    when(documentStore.read(getKey(AsyncKubePodStatus.FAILED))).thenReturn(Optional.of("output"));
    final var failedStatus = stateManager.getStatus(KUBE_POD_INFO);
    assertEquals(AsyncKubePodStatus.FAILED, failedStatus);
  }

  private static String getKey(final AsyncKubePodStatus status) {
    return DefaultAsyncStateManager.getDocumentStoreKey(KUBE_POD_INFO, status);
  }

}
