/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.process.AsyncKubePodStatus;
import io.airbyte.workers.process.AsyncOrchestratorPodProcess;
import io.airbyte.workers.process.KubePodInfo;
import io.airbyte.workers.process.KubeProcessFactory;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

/**
 * Coordinates configuring and managing the state of an async process. This is tied to the (job_id,
 * attempt_id) and will attempt to kill off lower attempt ids.
 *
 * @param <INPUT> a json-serializable input class for the worker
 * @param <OUTPUT> either {@link Void} or a json-serializable output class for the worker
 */
@Slf4j
public class LauncherWorker<INPUT, OUTPUT> implements Worker<INPUT, OUTPUT> {

  private final String application;
  private final String podNamePrefix;
  private final JobRunConfig jobRunConfig;
  private final Map<String, String> additionalFileMap;
  private final WorkerApp.ContainerOrchestratorConfig containerOrchestratorConfig;
  private final String airbyteVersion;
  private final ResourceRequirements resourceRequirements;
  private final Class<OUTPUT> outputClass;

  private final AtomicBoolean cancelled = new AtomicBoolean(false);
  private AsyncOrchestratorPodProcess process;

  public LauncherWorker(
                        final String application,
                        final String podNamePrefix,
                        final JobRunConfig jobRunConfig,
                        final Map<String, String> additionalFileMap,
                        final WorkerApp.ContainerOrchestratorConfig containerOrchestratorConfig,
                        final String airbyteVersion,
                        final ResourceRequirements resourceRequirements,
                        final Class<OUTPUT> outputClass) {
    this.application = application;
    this.podNamePrefix = podNamePrefix;
    this.jobRunConfig = jobRunConfig;
    this.additionalFileMap = additionalFileMap;
    this.containerOrchestratorConfig = containerOrchestratorConfig;
    this.airbyteVersion = airbyteVersion;
    this.resourceRequirements = resourceRequirements;
    this.outputClass = outputClass;
  }

  @Override
  public OUTPUT run(INPUT input, Path jobRoot) throws WorkerException {
    try {
      final Map<String, String> envMap = System.getenv().entrySet().stream()
          .filter(entry -> OrchestratorConstants.ENV_VARS_TO_TRANSFER.contains(entry.getKey()))
          .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

      final Map<String, String> fileMap = new HashMap<>(additionalFileMap);
      fileMap.putAll(Map.of(
          OrchestratorConstants.INIT_FILE_APPLICATION, application,
          OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG, Jsons.serialize(jobRunConfig),
          OrchestratorConstants.INIT_FILE_INPUT, Jsons.serialize(input),
          OrchestratorConstants.INIT_FILE_ENV_MAP, Jsons.serialize(envMap)));

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

      final var podNameAndJobPrefix = podNamePrefix + "-j-" + jobRunConfig.getJobId() + "-a-";
      killLowerAttemptIdsIfPresent(podNameAndJobPrefix, jobRunConfig.getAttemptId());

      final var podName = podNameAndJobPrefix + jobRunConfig.getAttemptId();
      final var kubePodInfo = new KubePodInfo(containerOrchestratorConfig.namespace(), podName);

      process = new AsyncOrchestratorPodProcess(
          kubePodInfo,
          containerOrchestratorConfig.documentStoreClient(),
          containerOrchestratorConfig.kubernetesClient());

      if (process.getDocStoreStatus().equals(AsyncKubePodStatus.NOT_STARTED)) {
        process.create(
            airbyteVersion,
            allLabels,
            resourceRequirements,
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
        return Jsons.deserialize(output.get(), outputClass);
      } else {
        throw new WorkerException("Running the " + application + " launcher resulted in no readable output!");
      }
    } catch (Exception e) {
      if (cancelled.get()) {
        throw new WorkerException("Launcher " + application + " was cancelled.", e);
      } else {
        throw new WorkerException("Running the launcher " + application + " failed", e);
      }
    }
  }

  /**
   * If the sync workflow has advanced to the next attempt, we don't want to leave a zombie of the
   * older job running (if it exists). In order to ensure a consistent state, we should kill the older
   * versions.
   */
  private void killLowerAttemptIdsIfPresent(final String podNameAndJobPrefix, final long currentAttempt) {
    for (long previousAttempt = currentAttempt - 1; previousAttempt >= 0; previousAttempt--) {
      final var podName = podNameAndJobPrefix + previousAttempt;
      final var kubePodInfo = new KubePodInfo(containerOrchestratorConfig.namespace(), podName);
      final var oldProcess = new AsyncOrchestratorPodProcess(
          kubePodInfo,
          containerOrchestratorConfig.documentStoreClient(),
          containerOrchestratorConfig.kubernetesClient());

      try {
        oldProcess.destroy();
        log.info("Found and destroyed a previous attempt: " + previousAttempt);
      } catch (Exception e) {
        log.warn("Wasn't able to find and destroy a previous attempt: " + previousAttempt);
      }
    }
  }

  @Override
  public void cancel() {
    cancelled.set(true);

    if (process == null) {
      return;
    }

    log.debug("Closing sync runner process");
    process.destroy();

    if (process.hasExited()) {
      log.info("Successfully cancelled process.");
    } else {
      // try again
      process.destroy();

      if (process.hasExited()) {
        log.info("Successfully cancelled process.");
      } else {
        log.error("Unable to cancel process");
      }
    }
  }

}
