/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Launches a container-orchestrator container/pod to manage the message passing for the replication
 * step. This step configs onto the container-orchestrator and retrieves logs and the output from
 * the container-orchestrator.
 */
public class ReplicationLauncherWorker implements Worker<StandardSyncInput, ReplicationOutput> {

  private static final Logger LOGGER = LoggerFactory.getLogger(ReplicationLauncherWorker.class);

  private static final MdcScope.Builder LOG_MDC_BUILDER = new MdcScope.Builder()
      .setLogPrefix("container-orchestrator")
      .setPrefixColor(LoggingHelper.Color.CYAN_BACKGROUND);

  public static final String REPLICATION = "replication";
  public static final String INIT_FILE_APPLICATION = "application.txt";
  public static final String INIT_FILE_JOB_RUN_CONFIG = "jobRunConfig.json";
  public static final String INIT_FILE_SOURCE_LAUNCHER_CONFIG = "sourceLauncherConfig.json";
  public static final String INIT_FILE_DESTINATION_LAUNCHER_CONFIG = "destinationLauncherConfig.json";
  public static final String INIT_FILE_SYNC_INPUT = "syncInput.json";
  public static final String INIT_FILE_ENV_MAP = "envMap.json";

  // define two ports for stdout/stderr usage on the container orchestrator pod
  public static final int PORT1 = 9877;
  public static final int PORT2 = 9878;
  public static final int PORT3 = 9879;
  public static final int PORT4 = 9880;
  public static final Set<Integer> PORTS = Set.of(PORT1, PORT2, PORT3, PORT4);

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

  private final AtomicBoolean cancelled = new AtomicBoolean(false);
  private final IntegrationLauncherConfig sourceLauncherConfig;
  private final IntegrationLauncherConfig destinationLauncherConfig;
  private final JobRunConfig jobRunConfig;
  private final StandardSyncInput syncInput;
  private final Path workspaceRoot;
  private final ProcessFactory processFactory;
  private final String airbyteVersion;
  private final WorkerConfigs workerConfigs;

  private Process process;

  public ReplicationLauncherWorker(
                                   final IntegrationLauncherConfig sourceLauncherConfig,
                                   final IntegrationLauncherConfig destinationLauncherConfig,
                                   final JobRunConfig jobRunConfig,
                                   final StandardSyncInput syncInput,
                                   final Path workspaceRoot,
                                   final ProcessFactory processFactory,
                                   final String airbyteVersion,
                                   final WorkerConfigs workerConfigs) {

    this.sourceLauncherConfig = sourceLauncherConfig;
    this.destinationLauncherConfig = destinationLauncherConfig;
    this.jobRunConfig = jobRunConfig;
    this.syncInput = syncInput;
    this.workspaceRoot = workspaceRoot;
    this.processFactory = processFactory;
    this.airbyteVersion = airbyteVersion;
    this.workerConfigs = workerConfigs;
  }

  @Override
  public ReplicationOutput run(StandardSyncInput standardSyncInput, Path jobRoot) throws WorkerException {
    try {
      final Path jobPath = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());

      // we want to filter down to remove secrets, so we aren't writing over a bunch of unnecessary
      // secrets
      final Map<String, String> envMap = System.getenv().entrySet().stream()
          .filter(entry -> ENV_VARS_TO_TRANSFER.contains(entry.getKey()))
          .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

      final Map<String, String> fileMap = Map.of(
          INIT_FILE_APPLICATION, REPLICATION,
          INIT_FILE_JOB_RUN_CONFIG, Jsons.serialize(jobRunConfig),
          INIT_FILE_SOURCE_LAUNCHER_CONFIG, Jsons.serialize(sourceLauncherConfig),
          INIT_FILE_DESTINATION_LAUNCHER_CONFIG, Jsons.serialize(destinationLauncherConfig),
          INIT_FILE_SYNC_INPUT, Jsons.serialize(syncInput),
          INIT_FILE_ENV_MAP, Jsons.serialize(envMap));

      process = processFactory.create(
          "runner-" + UUID.randomUUID().toString().substring(0, 10),
          0,
          jobPath,
          "airbyte/container-orchestrator:" + airbyteVersion,
          false,
          fileMap,
          null,
          workerConfigs.getResourceRequirements(),
          Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_RUNNER),
          Map.of(
              WorkerApp.KUBE_HEARTBEAT_PORT, WorkerApp.KUBE_HEARTBEAT_PORT,
              PORT1, PORT1,
              PORT2, PORT2,
              PORT3, PORT3,
              PORT4, PORT4));

      final AtomicReference<ReplicationOutput> output = new AtomicReference<>();

      LineGobbler.gobble(process.getInputStream(), line -> {
        final Optional<ReplicationOutput> maybeOutput = Jsons.tryDeserialize(line, ReplicationOutput.class);

        if (maybeOutput.isPresent()) {
          LOGGER.info("Found output!");
          output.set(maybeOutput.get());
        } else {
          try (final var mdcScope = LOG_MDC_BUILDER.build()) {
            LOGGER.info(line);
          }
        }
      });

      LineGobbler.gobble(process.getErrorStream(), LOGGER::error, LOG_MDC_BUILDER);

      WorkerUtils.wait(process);

      if (process.exitValue() != 0) {
        throw new WorkerException("Non-zero exit code!");
      }

      if (output.get() != null) {
        return output.get();
      } else {
        throw new WorkerException("Running the sync attempt resulted in no readable output!");
      }
    } catch (Exception e) {
      if (cancelled.get()) {
        throw new WorkerException("Sync was cancelled.", e);
      } else {
        throw new WorkerException("Running the sync attempt failed", e);
      }
    }
  }

  @Override
  public void cancel() {
    cancelled.set(true);

    if (process == null) {
      return;
    }

    LOGGER.debug("Closing sync runner process");
    WorkerUtils.gentleClose(workerConfigs, process, 1, TimeUnit.MINUTES);
    if (process.isAlive() || process.exitValue() != 0) {
      LOGGER.error("Sync runner process wasn't successful");
    }
  }

}
