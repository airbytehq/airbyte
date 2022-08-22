/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.process;

import io.fabric8.kubernetes.api.model.ContainerStatus;
import io.fabric8.kubernetes.api.model.Pod;
import java.util.List;
import java.util.stream.Collectors;

public class KubePodResourceHelper {

  public static boolean isTerminal(final Pod pod) {
    if (pod.getStatus() != null) {
      // Check if "main" container has terminated, as that defines whether the parent process has
      // terminated.
      final List<ContainerStatus> mainContainerStatuses = pod.getStatus()
          .getContainerStatuses()
          .stream()
          .filter(containerStatus -> containerStatus.getName().equals(KubePodProcess.MAIN_CONTAINER_NAME))
          .collect(Collectors.toList());

      return mainContainerStatuses.size() == 1 && mainContainerStatuses.get(0).getState() != null
          && mainContainerStatuses.get(0).getState().getTerminated() != null;
    } else {
      return false;
    }
  }

}
