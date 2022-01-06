/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubeProcessFactory;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
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

  public static final String REPLICATION = "replication";
  public static final String INIT_FILE_SOURCE_LAUNCHER_CONFIG = "sourceLauncherConfig.json";
  public static final String INIT_FILE_DESTINATION_LAUNCHER_CONFIG = "destinationLauncherConfig.json";

  private final AtomicBoolean cancelled = new AtomicBoolean(false);
  private final WorkerApp.ContainerOrchestratorConfig containerOrchestratorConfig;
  private final IntegrationLauncherConfig sourceLauncherConfig;
  private final IntegrationLauncherConfig destinationLauncherConfig;
  private final JobRunConfig jobRunConfig;
  private final StandardSyncInput syncInput;
  private final String airbyteVersion;
  private final WorkerConfigs workerConfigs;

  private AsyncOrchestratorPodProcess process;

  public ReplicationLauncherWorker(
                                   final WorkerApp.ContainerOrchestratorConfig containerOrchestratorConfig,
                                   final IntegrationLauncherConfig sourceLauncherConfig,
                                   final IntegrationLauncherConfig destinationLauncherConfig,
                                   final JobRunConfig jobRunConfig,
                                   final StandardSyncInput syncInput,
                                   final Path workspaceRoot,
                                   final String airbyteVersion,
                                   final WorkerConfigs workerConfigs) {
    this.containerOrchestratorConfig = containerOrchestratorConfig;
    this.sourceLauncherConfig = sourceLauncherConfig;
    this.destinationLauncherConfig = destinationLauncherConfig;
    this.jobRunConfig = jobRunConfig;
    this.syncInput = syncInput;
    this.airbyteVersion = airbyteVersion;
    this.workerConfigs = workerConfigs;
  }

  @Override
  public ReplicationOutput run(StandardSyncInput standardSyncInput, Path jobRoot) throws WorkerException {
    try {
      final Map<String, String> envMap = System.getenv().entrySet().stream()
          .filter(entry -> OrchestratorConstants.ENV_VARS_TO_TRANSFER.contains(entry.getKey()))
          .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

      final Map<String, String> fileMap = Map.of(
          OrchestratorConstants.INIT_FILE_APPLICATION, REPLICATION,
          OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG, Jsons.serialize(jobRunConfig),
          OrchestratorConstants.INIT_FILE_INPUT, Jsons.serialize(syncInput),
          OrchestratorConstants.INIT_FILE_ENV_MAP, Jsons.serialize(envMap),
          INIT_FILE_SOURCE_LAUNCHER_CONFIG, Jsons.serialize(sourceLauncherConfig),
          INIT_FILE_DESTINATION_LAUNCHER_CONFIG, Jsons.serialize(destinationLauncherConfig));

      final Map<Integer, Integer> portMap = Map.of(
          WorkerApp.KUBE_HEARTBEAT_PORT, WorkerApp.KUBE_HEARTBEAT_PORT,
          OrchestratorConstants.PORT1, OrchestratorConstants.PORT1,
          OrchestratorConstants.PORT2, OrchestratorConstants.PORT2,
          OrchestratorConstants.PORT3, OrchestratorConstants.PORT3,
          OrchestratorConstants.PORT4, OrchestratorConstants.PORT4);

      final var allLabels = KubeProcessFactory.getLabels(
          jobRunConfig.getJobId(),
          Math.toIntExact(jobRunConfig.getAttemptId()),
          Collections.emptyMap());

      final var podName = "orchestrator-repl-j-" + jobRunConfig.getJobId() + "-a-" + jobRunConfig.getAttemptId();
      final var kubePodInfo = new KubePodInfo(containerOrchestratorConfig.namespace(), podName);

      process = new AsyncOrchestratorPodProcess(
          kubePodInfo,
          containerOrchestratorConfig.documentStoreClient(),
          containerOrchestratorConfig.kubernetesClient());

      if (process.getDocStoreStatus().equals(AsyncKubePodStatus.NOT_STARTED)) {
        process.create(
            airbyteVersion,
            allLabels,
            workerConfigs.getResourceRequirements(),
            fileMap,
            portMap);
      }

      // this waitFor can resume if the activity is re-run
      process.waitFor();

      if (process.exitValue() != 0) {
        throw new WorkerException("Non-zero exit code!");
      }

      final var output = process.getOutput();

      if (output.isPresent()) {
        return Jsons.deserialize(output.get(), ReplicationOutput.class);
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
    process.destroy();

    if (process.hasExited()) {
      LOGGER.info("Successfully cancelled process.");
    } else {
      // try again
      process.destroy();

      if (process.hasExited()) {
        LOGGER.info("Successfully cancelled process.");
      } else {
        LOGGER.error("Unable to cancel process");
      }
    }
  }

}
