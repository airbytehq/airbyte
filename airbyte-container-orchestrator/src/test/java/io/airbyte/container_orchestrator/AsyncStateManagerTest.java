/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.KubeContainerInfo;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.storage.DocumentStoreClient;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class AsyncStateManagerTest {

  public static final String FAKE_IMAGE = "fake_image";
  private static final KubePodInfo KUBE_POD_INFO = new KubePodInfo("default", "pod1",
      new KubeContainerInfo(FAKE_IMAGE, "IfNotPresent"));
  private static final String OUTPUT = "some output value";

  private DocumentStoreClient documentStore;
  private AsyncStateManager stateManager;

  @BeforeEach
  void setup() {
    documentStore = mock(DocumentStoreClient.class);
    stateManager = new AsyncStateManager(documentStore, KUBE_POD_INFO);
  }

  @Test
  void testEmptyWrite() {
    stateManager.write(AsyncKubePodStatus.INITIALIZING);

    // test for overwrite (which should be allowed)
    stateManager.write(AsyncKubePodStatus.INITIALIZING);

    final var key = stateManager.getDocumentStoreKey(AsyncKubePodStatus.INITIALIZING);
    verify(documentStore, times(2)).write(key, "");
  }

  @Test
  void testContentfulWrite() {
    stateManager.write(AsyncKubePodStatus.SUCCEEDED, OUTPUT);

    final var key = stateManager.getDocumentStoreKey(AsyncKubePodStatus.SUCCEEDED);
    verify(documentStore, times(1)).write(key, OUTPUT);
  }

  @Test
  void testReadingOutputWhenItExists() {
    final var key = stateManager.getDocumentStoreKey(AsyncKubePodStatus.SUCCEEDED);
    when(documentStore.read(key)).thenReturn(Optional.of(OUTPUT));
    assertEquals(OUTPUT, stateManager.getOutput());
  }

  @Test
  void testReadingOutputWhenItDoesNotExist() {
    // getting the output should throw an exception when there is no record in the document store
    assertThrows(IllegalArgumentException.class, () -> {
      stateManager.getOutput();
    });
  }

  @Test
  void testSuccessfulStatusRetrievalLifecycle() {
    when(documentStore.read(stateManager.getDocumentStoreKey(AsyncKubePodStatus.INITIALIZING))).thenReturn(Optional.empty());
    final var beforeInitializingStatus = stateManager.getStatus();
    assertEquals(AsyncKubePodStatus.NOT_STARTED, beforeInitializingStatus);

    when(documentStore.read(stateManager.getDocumentStoreKey(AsyncKubePodStatus.INITIALIZING))).thenReturn(Optional.of(""));
    final var initializingStatus = stateManager.getStatus();
    assertEquals(AsyncKubePodStatus.INITIALIZING, initializingStatus);

    when(documentStore.read(stateManager.getDocumentStoreKey(AsyncKubePodStatus.RUNNING))).thenReturn(Optional.of(""));
    final var runningStatus = stateManager.getStatus();
    assertEquals(AsyncKubePodStatus.RUNNING, runningStatus);

    when(documentStore.read(stateManager.getDocumentStoreKey(AsyncKubePodStatus.SUCCEEDED))).thenReturn(
        Optional.of("output"));
    final var succeededStatus = stateManager.getStatus();
    assertEquals(AsyncKubePodStatus.SUCCEEDED, succeededStatus);
  }

  @Test
  void testFailureStatusRetrievalLifecycle() {
    when(documentStore.read(stateManager.getDocumentStoreKey(AsyncKubePodStatus.INITIALIZING))).thenReturn(Optional.empty());
    final var beforeInitializingStatus = stateManager.getStatus();
    assertEquals(AsyncKubePodStatus.NOT_STARTED, beforeInitializingStatus);

    when(documentStore.read(stateManager.getDocumentStoreKey(AsyncKubePodStatus.INITIALIZING))).thenReturn(Optional.of(""));
    final var initializingStatus = stateManager.getStatus();
    assertEquals(AsyncKubePodStatus.INITIALIZING, initializingStatus);

    when(documentStore.read(stateManager.getDocumentStoreKey(AsyncKubePodStatus.RUNNING))).thenReturn(Optional.of(""));
    final var runningStatus = stateManager.getStatus();
    assertEquals(AsyncKubePodStatus.RUNNING, runningStatus);

    when(documentStore.read(stateManager.getDocumentStoreKey(AsyncKubePodStatus.FAILED))).thenReturn(Optional.of("output"));
    final var failedStatus = stateManager.getStatus();
    assertEquals(AsyncKubePodStatus.FAILED, failedStatus);
  }

}
