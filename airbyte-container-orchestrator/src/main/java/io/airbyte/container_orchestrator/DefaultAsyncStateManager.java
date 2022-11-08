/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.storage.DocumentStoreClient;
import java.util.List;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DefaultAsyncStateManager implements AsyncStateManager {

  private static final List<AsyncKubePodStatus> STATUS_CHECK_ORDER = List.of(
      // terminal states first
      AsyncKubePodStatus.FAILED,
      AsyncKubePodStatus.SUCCEEDED,

      // then check in progress state
      AsyncKubePodStatus.RUNNING,

      // then check for initialization state
      AsyncKubePodStatus.INITIALIZING);

  private final DocumentStoreClient documentStoreClient;

  public DefaultAsyncStateManager(final DocumentStoreClient documentStoreClient) {
    this.documentStoreClient = documentStoreClient;
  }

  @Override
  public void write(final KubePodInfo kubePodInfo, final AsyncKubePodStatus status, final String value) {
    final var key = getDocumentStoreKey(kubePodInfo, status);
    log.info("Writing async status {} for {}...", status, kubePodInfo);
    documentStoreClient.write(key, value);
  }

  @Override
  public void write(final KubePodInfo kubePodInfo, final AsyncKubePodStatus status) {
    write(kubePodInfo, status, "");
  }

  /**
   * Checks terminal states first, then running, then initialized. Defaults to not started.
   *
   * The order matters here!
   */
  @Override
  public AsyncKubePodStatus getStatus(KubePodInfo kubePodInfo) {
    for (AsyncKubePodStatus status : STATUS_CHECK_ORDER) {
      if (statusFileExists(kubePodInfo, status)) {
        return status;
      }
    }

    return AsyncKubePodStatus.NOT_STARTED;
  }

  @Override
  public String getOutput(KubePodInfo kubePodInfo) throws IllegalArgumentException {
    final var key = getDocumentStoreKey(kubePodInfo, AsyncKubePodStatus.SUCCEEDED);
    final var output = documentStoreClient.read(key);

    if (output.isPresent()) {
      return output.get();
    } else {
      throw new IllegalArgumentException("Expected to retrieve output from a successfully completed pod!");
    }
  }

  /**
   * IMPORTANT: Changing the storage location will orphan already existing kube pods when the new
   * version is deployed!
   */
  public static String getDocumentStoreKey(final KubePodInfo kubePodInfo, final AsyncKubePodStatus status) {
    return kubePodInfo.namespace() + "/" + kubePodInfo.name() + "/" + status.name();
  }

  private boolean statusFileExists(final KubePodInfo kubePodInfo, final AsyncKubePodStatus status) {
    final var key = getDocumentStoreKey(kubePodInfo, status);
    return documentStoreClient.read(key).isPresent();
  }

}
