/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.OperatorDbtInput;
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

// todo: DRY the launchers
public class DbtLauncherWorker implements Worker<OperatorDbtInput, Void> {

  private static final Logger LOGGER = LoggerFactory.getLogger(DbtLauncherWorker.class);

  public static final String DBT = "dbt-orchestrator";
  public static final String INIT_FILE_DESTINATION_LAUNCHER_CONFIG = "destinationLauncherConfig.json";

  private final WorkerConfigs workerConfigs;
  private final WorkerApp.ContainerOrchestratorConfig containerOrchestratorConfig;
  private final String airbyteVersion;
  private final Path workspaceRoot;
  private final IntegrationLauncherConfig destinationLauncherConfig;
  private final JobRunConfig jobRunConfig;

  private final AtomicBoolean cancelled = new AtomicBoolean(false);

  private AsyncOrchestratorPodProcess process;

  public DbtLauncherWorker(
                           final Path workspaceRoot,
                           final IntegrationLauncherConfig destinationLauncherConfig,
                           final JobRunConfig jobRunConfig,
                           final WorkerConfigs workerConfigs,
                           final WorkerApp.ContainerOrchestratorConfig containerOrchestratorConfig,
                           final String airbyteVersion) {
    this.workspaceRoot = workspaceRoot;
    this.destinationLauncherConfig = destinationLauncherConfig;
    this.jobRunConfig = jobRunConfig;
    this.workerConfigs = workerConfigs;
    this.containerOrchestratorConfig = containerOrchestratorConfig;
    this.airbyteVersion = airbyteVersion;
  }

  // todo: DRY with other launcher workers
  @Override
  public Void run(OperatorDbtInput operatorDbtInput, Path jobRoot) throws WorkerException {
    try {
      final Map<String, String> envMap = System.getenv().entrySet().stream()
          .filter(entry -> OrchestratorConstants.ENV_VARS_TO_TRANSFER.contains(entry.getKey()))
          .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

      final Map<String, String> fileMap = Map.of(
          OrchestratorConstants.INIT_FILE_APPLICATION, DBT,
          OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG, Jsons.serialize(jobRunConfig),
          OrchestratorConstants.INIT_FILE_INPUT, Jsons.serialize(operatorDbtInput),
          OrchestratorConstants.INIT_FILE_ENV_MAP, Jsons.serialize(envMap),
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

      final var podName = "orchestrator-dbt-j-" + jobRunConfig.getJobId() + "-a-" + jobRunConfig.getAttemptId();
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

      return null;
    } catch (Exception e) {
      if (cancelled.get()) {
        throw new WorkerException("Dbt was cancelled.", e);
      } else {
        throw new WorkerException("Running dbt failed", e);
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
