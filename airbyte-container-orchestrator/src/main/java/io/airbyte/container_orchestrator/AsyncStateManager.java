/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.KubePodInfo;

/**
 * The state manager writes the "truth" for states of the async pod process. If the store isn't
 * updated by the underlying pod, it will appear as failed.
 *
 * It doesn't have a single value for a state. Instead, in a location on cloud storage or disk, it
 * writes every state it's encountered.
 */
public interface AsyncStateManager {

  /**
   * Writes a file containing a string value to a location designated by the input status.
   */
  void write(final KubePodInfo kubePodInfo, final AsyncKubePodStatus status, final String value);

  /**
   * Writes an empty file to a location designated by the input status.
   */
  void write(final KubePodInfo kubePodInfo, final AsyncKubePodStatus status);

  /**
   * Interprets the state given all written state messages for the pod.
   */
  AsyncKubePodStatus getStatus(final KubePodInfo kubePodInfo);

  /**
   * @return the output stored in the success file. This can be an empty string.
   * @throws IllegalArgumentException if no success file exists
   */
  String getOutput(final KubePodInfo kubePodInfo) throws IllegalArgumentException;

}
