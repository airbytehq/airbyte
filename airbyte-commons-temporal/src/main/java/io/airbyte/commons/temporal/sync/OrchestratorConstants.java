/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.sync;

import com.uber.m3.util.ImmutableSet;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import java.util.Set;

public class OrchestratorConstants {

  // we want to propagate log level, even if it isn't consumed by EnvConfigs
  private static final String LOG_LEVEL = "LOG_LEVEL";

  // necessary for s3/minio logging. used in the log4j2 configuration.
  private static final String S3_PATH_STYLE_ACCESS = "S3_PATH_STYLE_ACCESS";
  private static final String FEATURE_FLAG_CLIENT = "FEATURE_FLAG_CLIENT";
  private static final String FEATURE_FLAG_PATH = "FEATURE_FLAG_PATH";
  private static final String LAUNCHDARKLY_KEY = "LAUNCHDARKLY_KEY";

  // set of env vars necessary for the container orchestrator app to run
  public static final Set<String> ENV_VARS_TO_TRANSFER = new ImmutableSet.Builder<String>()
      .addAll(EnvConfigs.JOB_SHARED_ENVS.keySet())
      .addAll(Set.of(
          EnvConfigs.WORKER_ENVIRONMENT,
          EnvConfigs.JOB_KUBE_TOLERATIONS,
          EnvConfigs.JOB_KUBE_CURL_IMAGE,
          EnvConfigs.JOB_KUBE_BUSYBOX_IMAGE,
          EnvConfigs.JOB_KUBE_SOCAT_IMAGE,
          EnvConfigs.JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY,
          EnvConfigs.JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET,
          EnvConfigs.JOB_KUBE_SIDECAR_CONTAINER_IMAGE_PULL_POLICY,
          EnvConfigs.JOB_KUBE_NODE_SELECTORS,
          EnvConfigs.JOB_ISOLATED_KUBE_NODE_SELECTORS,
          EnvConfigs.USE_CUSTOM_NODE_SELECTOR,
          EnvConfigs.DOCKER_NETWORK,
          EnvConfigs.LOCAL_DOCKER_MOUNT,
          EnvConfigs.WORKSPACE_DOCKER_MOUNT,
          EnvConfigs.WORKSPACE_ROOT,
          EnvConfigs.JOB_KUBE_NAMESPACE,
          EnvConfigs.JOB_MAIN_CONTAINER_CPU_REQUEST,
          EnvConfigs.JOB_MAIN_CONTAINER_CPU_LIMIT,
          EnvConfigs.JOB_MAIN_CONTAINER_MEMORY_REQUEST,
          EnvConfigs.JOB_MAIN_CONTAINER_MEMORY_LIMIT,
          EnvConfigs.JOB_DEFAULT_ENV_MAP,
          EnvConfigs.LOCAL_ROOT,
          EnvConfigs.PUBLISH_METRICS,
          EnvConfigs.DD_AGENT_HOST,
          EnvConfigs.DD_DOGSTATSD_PORT,
          EnvConfigs.METRIC_CLIENT,
          LOG_LEVEL,
          LogClientSingleton.GCS_LOG_BUCKET,
          LogClientSingleton.GOOGLE_APPLICATION_CREDENTIALS,
          LogClientSingleton.S3_MINIO_ENDPOINT,
          S3_PATH_STYLE_ACCESS,
          LogClientSingleton.S3_LOG_BUCKET,
          LogClientSingleton.AWS_ACCESS_KEY_ID,
          LogClientSingleton.AWS_SECRET_ACCESS_KEY,
          LogClientSingleton.S3_LOG_BUCKET_REGION,
          EnvConfigs.STATE_STORAGE_GCS_BUCKET_NAME,
          EnvConfigs.STATE_STORAGE_GCS_APPLICATION_CREDENTIALS,
          EnvConfigs.STATE_STORAGE_MINIO_ENDPOINT,
          EnvConfigs.STATE_STORAGE_MINIO_BUCKET_NAME,
          EnvConfigs.STATE_STORAGE_MINIO_ACCESS_KEY,
          EnvConfigs.STATE_STORAGE_MINIO_SECRET_ACCESS_KEY,
          EnvConfigs.STATE_STORAGE_S3_BUCKET_NAME,
          EnvConfigs.STATE_STORAGE_S3_ACCESS_KEY,
          EnvConfigs.STATE_STORAGE_S3_SECRET_ACCESS_KEY,
          EnvConfigs.STATE_STORAGE_S3_REGION,
          EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE,
          EnvVariableFeatureFlags.AUTO_DETECT_SCHEMA,
          EnvVariableFeatureFlags.APPLY_FIELD_SELECTION,
          EnvVariableFeatureFlags.FIELD_SELECTION_WORKSPACES,
          FEATURE_FLAG_CLIENT,
          FEATURE_FLAG_PATH,
          LAUNCHDARKLY_KEY,
          EnvConfigs.SOCAT_KUBE_CPU_LIMIT,
          EnvConfigs.SOCAT_KUBE_CPU_REQUEST))
      .build();

  public static final String INIT_FILE_ENV_MAP = "envMap.json";
  public static final String INIT_FILE_INPUT = "input.json";
  public static final String INIT_FILE_JOB_RUN_CONFIG = "jobRunConfig.json";
  public static final String INIT_FILE_APPLICATION = "application.txt";

  // define two ports for stdout/stderr usage on the container orchestrator pod
  public static final int PORT1 = 9877;
  public static final int PORT2 = 9878;
  public static final int PORT3 = 9879;
  public static final int PORT4 = 9880;
  public static final Set<Integer> PORTS = Set.of(PORT1, PORT2, PORT3, PORT4);

}
