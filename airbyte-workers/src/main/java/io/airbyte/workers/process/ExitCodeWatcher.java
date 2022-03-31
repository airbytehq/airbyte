/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import com.google.common.collect.MoreCollectors;
import io.fabric8.kubernetes.api.model.ContainerStatus;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.client.Watcher;
import io.fabric8.kubernetes.client.WatcherException;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;

/**
 * The exit code watcher uses the Kubernetes watch API, which provides a subscription to events for
 * a pod. This subscription has better latency than polling at the expense of keeping a connection
 * open with the Kubernetes API server. Since it offers all events, it helps us handle cases like
 * where a pod is swept or deleted immediately after running on a Kubernetes cluster (we will still
 * be able to retrieve the exit code).
 */
@Slf4j
public class ExitCodeWatcher implements Watcher<Pod> {

  private final Consumer<Integer> onExitCode;
  private final Consumer<WatcherException> onWatchFailure;
  private boolean exitCodeRetrieved = false;

  /**
   *
   * @param onExitCode callback used to store the exit code
   * @param onWatchFailure callback that's triggered when the watch fails. should be some failed exit
   *        code.
   */
  public ExitCodeWatcher(final Consumer<Integer> onExitCode, final Consumer<WatcherException> onWatchFailure) {
    this.onExitCode = onExitCode;
    this.onWatchFailure = onWatchFailure;
  }

  @Override
  public void eventReceived(Action action, Pod resource) {
    try {
      if (!exitCodeRetrieved && KubePodResourceHelper.isTerminal(resource)) {
        final ContainerStatus mainContainerStatus = resource.getStatus().getContainerStatuses()
            .stream()
            .filter(containerStatus -> containerStatus.getName().equals(KubePodProcess.MAIN_CONTAINER_NAME))
            .collect(MoreCollectors.onlyElement());

        if (mainContainerStatus.getState() != null && mainContainerStatus.getState().getTerminated() != null) {
          final int exitCode = mainContainerStatus.getState().getTerminated().getExitCode();
          log.info("Processing event with exit code " + exitCode + " for pod: " + resource.getMetadata().getName());
          onExitCode.accept(exitCode);
          exitCodeRetrieved = true;
        }
      }
    } catch (Exception e) {
      String podName = "<unknown_name>";
      if (resource.getMetadata() != null) {
        podName = resource.getMetadata().getName();
      }

      log.error("ExitCodeWatcher event handling failed for pod: " + podName, e);
    }
  }

  @Override
  public void onClose(WatcherException cause) {
    onWatchFailure.accept(cause);
  }

}
