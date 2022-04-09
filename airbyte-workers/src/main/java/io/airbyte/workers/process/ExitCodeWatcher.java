/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import com.google.common.collect.MoreCollectors;
import io.fabric8.kubernetes.api.model.ContainerStatus;
import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.client.informers.ResourceEventHandler;
import java.util.Objects;
import java.util.Optional;
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
public class ExitCodeWatcher implements ResourceEventHandler<Pod> {

  private final String podName;
  private final String podNamespace;
  private final Consumer<Integer> onExitCode;
  private final Runnable onWatchFailure;
  /**
   * This flag is set to false when we either (a) find the pod's exit code, or (b) when the pod is
   * deleted. This is so that we call exactly one of onExitCode and onWatchFailure, and we make that
   * call exactly once.
   */
  private boolean active = true;

  /**
   * @param onExitCode callback used to store the exit code
   * @param onWatchFailure callback that's triggered when the watch fails. should be some failed exit
   *        code.
   */
  public ExitCodeWatcher(final String podName,
                         final String podNamespace,
                         final Consumer<Integer> onExitCode,
                         final Runnable onWatchFailure) {
    this.podName = podName;
    this.podNamespace = podNamespace;
    this.onExitCode = onExitCode;
    this.onWatchFailure = onWatchFailure;
  }

  @Override
  public void onAdd(final Pod pod) {
    if (shouldCheckPod(pod)) {
      final Optional<Integer> exitCode = getExitCode(pod);
      exitCode.ifPresent(this::persistExitCode);
    }
  }

  @Override
  public void onUpdate(final Pod oldPod, final Pod newPod) {
    if (shouldCheckPod(newPod)) {
      final Optional<Integer> exitCode = getExitCode(newPod);
      exitCode.ifPresent(this::persistExitCode);
    }
  }

  @Override
  public void onDelete(final Pod pod, final boolean deletedFinalStateUnknown) {
    if (shouldCheckPod(pod)) {
      if (!deletedFinalStateUnknown) {
        final Optional<Integer> exitCode = getExitCode(pod);
        exitCode.ifPresentOrElse(
            this::persistExitCode,
            this::persistFailure);
      } else {
        persistFailure();
      }
    }
  }

  /**
   * This class will receive events for ALL pods in ALL namespaces; filter down to the one pod that we
   * care about. If it's still running, then we obviously can't fetch its exit code.
   * <p>
   * Also, if we've already found the exit code, or the pod has been deleted, then stop doing anything
   * at all.
   */
  private boolean shouldCheckPod(final Pod pod) {
    // Use Objects.equals in case the namespace is null
    final boolean correctName = Objects.equals(podNamespace, pod.getMetadata().getNamespace());
    final boolean correctNamespace = Objects.equals(podName, pod.getMetadata().getName());
    return active && correctName && correctNamespace && KubePodResourceHelper.isTerminal(pod);
  }

  private Optional<Integer> getExitCode(final Pod pod) {
    final ContainerStatus mainContainerStatus = pod.getStatus().getContainerStatuses()
        .stream()
        .filter(containerStatus -> containerStatus.getName().equals(KubePodProcess.MAIN_CONTAINER_NAME))
        .collect(MoreCollectors.onlyElement());

    if (mainContainerStatus.getState() != null && mainContainerStatus.getState().getTerminated() != null) {
      return Optional.of(mainContainerStatus.getState().getTerminated().getExitCode());
    }
    return Optional.empty();
  }

  private void persistExitCode(final int exitCode) {
    log.info("Received exit code {} for pod {}", exitCode, podName);
    onExitCode.accept(exitCode);
    active = false;
  }

  private void persistFailure() {
    // shut ourselves down and log an error. the pod is completely gone, and we have no way to retrieve
    // its exit code
    active = false;
    log.error("Pod {} was deleted before we could retrieve its exit code", podName);
    onWatchFailure.run();
  }

}
