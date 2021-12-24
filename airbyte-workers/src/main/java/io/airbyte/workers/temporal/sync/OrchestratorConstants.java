/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.config.EnvConfigs;
import java.util.Set;

public class OrchestratorConstants {

  // set of env vars necessary for the container orchestrator app to run
  public static final Set<String> ENV_VARS_TO_TRANSFER = Set.of(
      EnvConfigs.WORKER_ENVIRONMENT,
      EnvConfigs.JOB_KUBE_TOLERATIONS,
      EnvConfigs.JOB_KUBE_CURL_IMAGE,
      EnvConfigs.JOB_KUBE_BUSYBOX_IMAGE,
      EnvConfigs.JOB_KUBE_SOCAT_IMAGE,
      EnvConfigs.JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY,
      EnvConfigs.JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET,
      EnvConfigs.JOB_KUBE_NODE_SELECTORS,
      EnvConfigs.DOCKER_NETWORK,
      EnvConfigs.LOCAL_DOCKER_MOUNT,
      EnvConfigs.WORKSPACE_DOCKER_MOUNT,
      EnvConfigs.WORKSPACE_ROOT,
      EnvConfigs.DEFAULT_JOB_KUBE_NAMESPACE,
      EnvConfigs.JOB_MAIN_CONTAINER_CPU_REQUEST,
      EnvConfigs.JOB_MAIN_CONTAINER_CPU_LIMIT,
      EnvConfigs.JOB_MAIN_CONTAINER_MEMORY_REQUEST,
      EnvConfigs.JOB_MAIN_CONTAINER_MEMORY_LIMIT,
      EnvConfigs.LOCAL_ROOT);

  public static final String INIT_FILE_ENV_MAP = "envMap.json";
  public static final String INIT_FILE_INPUT = "input.json";

}
