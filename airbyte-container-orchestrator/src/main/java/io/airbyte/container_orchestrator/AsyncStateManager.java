/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.KubePodInfo;

public interface AsyncStateManager {

  void write(final KubePodInfo kubePodInfo, final AsyncKubePodStatus status, final String value);

  void write(final KubePodInfo kubePodInfo, final AsyncKubePodStatus status);

  AsyncKubePodStatus getStatus(final KubePodInfo kubePodInfo);

  String getOutput(final KubePodInfo kubePodInfo) throws IllegalArgumentException;

}
